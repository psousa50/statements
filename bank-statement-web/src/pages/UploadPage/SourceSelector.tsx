import React from 'react';
import { Button } from 'react-bootstrap';
import type { Source } from '../../types';

type Props = {
  sources: Source[];
  selectedSource?: Source;
  sourceId?: number;
  sourcePopupOpen: boolean;
  hoveredSource: number | null;
  onButtonClick: () => void;
  onOptionClick: (id: number) => void;
  onMouseEnter: (id: number) => void;
  onMouseLeave: () => void;
  menuStyle: React.CSSProperties;
  menuItemStyle: (highlighted: boolean) => React.CSSProperties;
  fullWidthPanelStyle: React.CSSProperties;
};

export default function SourceSelector({
  sources,
  selectedSource,
  sourceId,
  sourcePopupOpen,
  hoveredSource,
  onButtonClick,
  onOptionClick,
  onMouseEnter,
  onMouseLeave,
  menuStyle,
  menuItemStyle,
  fullWidthPanelStyle,
}: Props) {
  return (
    <div data-testid="source-selector-panel" style={{ ...fullWidthPanelStyle, height: '100%', display: 'flex', alignItems: 'stretch', justifyContent: 'center', padding: 0 }}>
      <div style={{ position: 'relative', width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Button
          data-testid="source-selector-btn"
          variant="outline-secondary"
          aria-haspopup="menu"
          aria-expanded={sourcePopupOpen}
          onClick={onButtonClick}
          style={{ minWidth: 180, }}
        >
          {`Source: ${selectedSource ? selectedSource.name : ''}`}
        </Button>
        {sourcePopupOpen && (
          <ul
            data-testid="source-selector-menu"
            role="menu"
            style={menuStyle}
          >
            {sources?.map((source) => (
              <li
                key={source.id}
                role="menuitem"
                aria-selected={sourceId === source.id}
                tabIndex={0}
                style={menuItemStyle(hoveredSource === source.id)}
                onMouseEnter={() => onMouseEnter(source.id)}
                onMouseLeave={onMouseLeave}
                onClick={() => onOptionClick(source.id)}
                onKeyDown={e => { if (e.key === 'Enter' || e.key === ' ') onOptionClick(source.id); }}
                className={hoveredSource === source.id ? 'highlighted' : ''}
              >
                {source.name}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
