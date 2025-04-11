import csv
import io
from typing import Callable, List, Optional

from fastapi import APIRouter, File, HTTPException, UploadFile

from ..models import Source
from ..repositories.sources_repository import SourcesRepository
from ..schemas import Source as SourceSchema
from ..schemas import SourceCreate


class SourceRouter:
    def __init__(
        self,
        source_repository: SourcesRepository,
        on_change_callback: Optional[Callable[[str, List[Source]], None]] = None,
    ):
        self.router = APIRouter(
            prefix="/sources",
            tags=["sources"],
        )
        self.source_repository = source_repository
        self.on_change_callback = on_change_callback

        # Register routes with trailing slashes removed
        self.router.add_api_route(
            "", self.get_sources, methods=["GET"], response_model=List[SourceSchema]
        )
        self.router.add_api_route(
            "/{source_id}",
            self.get_source,
            methods=["GET"],
            response_model=SourceSchema,
        )
        self.router.add_api_route(
            "", self.create_source, methods=["POST"], response_model=SourceSchema
        )
        self.router.add_api_route(
            "/{source_id}",
            self.update_source,
            methods=["PUT"],
            response_model=SourceSchema,
        )
        self.router.add_api_route(
            "/{source_id}", self.delete_source, methods=["DELETE"], status_code=204
        )
        self.router.add_api_route(
            "/import",
            self.import_sources_from_csv,
            methods=["POST"],
            status_code=201,
        )

    def _notify_change(self, action: str, sources: List[Source]):
        if self.on_change_callback:
            self.on_change_callback(action, sources)

    async def get_sources(
        self,
        skip: int = 0,
        limit: int = 100,
    ):
        sources = self.source_repository.get_all(skip, limit)
        return sources

    async def get_source(
        self,
        source_id: int,
    ):
        source = self.source_repository.get_by_id(source_id)
        if source is None:
            raise HTTPException(status_code=404, detail="Source not found")
        return source

    async def create_source(
        self,
        source: SourceCreate,
    ):
        # Check if source with the same name already exists
        db_source = self.source_repository.get_by_name(source.name)
        if db_source:
            raise HTTPException(
                status_code=400, detail="Source with this name already exists"
            )

        # Create the source using the repository
        new_source = self.source_repository.create(source)

        # Notify about the change
        self._notify_change("create", [new_source])

        return new_source

    async def update_source(
        self,
        source_id: int,
        source: SourceCreate,
    ):
        # Get the source to update
        db_source = self.source_repository.get_by_id(source_id)
        if db_source is None:
            raise HTTPException(status_code=404, detail="Source not found")

        # Check if another source with the same name already exists
        existing_source = self.source_repository.get_by_name(source.name)
        if existing_source:
            raise HTTPException(
                status_code=400, detail="Source with this name already exists"
            )

        # Update source
        for key, value in source.model_dump().items():
            setattr(db_source, key, value)

        self.source_repository.update(db_source)

        # Notify about the change
        self._notify_change("update", [db_source])

        return db_source

    async def delete_source(
        self,
        source_id: int,
    ):
        # Get the source to delete
        db_source = self.source_repository.get_by_id(source_id)
        if db_source is None:
            raise HTTPException(status_code=404, detail="Source not found")

        # Check if source is the default "unknown" source
        if db_source.name == "unknown":
            raise HTTPException(
                status_code=400, detail="Cannot delete the default 'unknown' source"
            )

        # Check if source has transactions
        if db_source.transactions:
            raise HTTPException(
                status_code=400, detail="Cannot delete a source that has transactions"
            )

        # Delete source
        self.source_repository.delete(db_source)

        # Notify about the change
        self._notify_change("delete", [db_source])

        return None

    async def import_sources_from_csv(self, file: UploadFile = File(...)):
        """Import sources from a CSV file"""
        try:
            contents = await file.read()
            csv_file = io.StringIO(contents.decode("utf-8"))
            csv_reader = csv.reader(csv_file)

            # Skip header row
            next(csv_reader)

            sources_created = []

            for row in csv_reader:
                if not row or not row[0].strip():
                    continue

                # Extract source data
                name = row[0].strip()
                description = row[1].strip() if len(row) > 1 else None

                # Check if source already exists
                existing_source = self.source_repository.get_by_name(name)
                if not existing_source:
                    # Create new source
                    new_source = Source(name=name, description=description)
                    new_source = self.source_repository.create(new_source)
                    sources_created.append(new_source)

            if sources_created:
                self._notify_change("import", sources_created)

            return {"message": f"Successfully imported {len(sources_created)} sources"}

        except Exception as e:
            self.source_repository.rollback()
            raise HTTPException(
                status_code=400, detail=f"Error importing sources: {str(e)}"
            )
