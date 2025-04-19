import { useState } from 'react';
import { Button } from 'react-bootstrap';
import type { Source } from '../../types';

type Props = {
  sources: Source[];
  selectedSource?: Source;
  sourceId?: number;
  sourcePopupOpen: boolean;
  onButtonClick: () => void;
  onOptionClick: (id: number) => void;
  onMouseEnter: (id: number) => void;
  onMouseLeave: () => void;
};

export default function SourceSelector({
  sources,
  selectedSource,
  sourceId,
  sourcePopupOpen,
  onButtonClick,
  onOptionClick,
  onMouseEnter,
  onMouseLeave,
}: Props) {
  const [hoveredSource, setHoveredSource] = useState<number | null>(null);

  return (
    <div data-testid="source-selector-panel" style={{
      width: '100%',
      border: '1px solid #ccc',
      padding: '1.2rem 2rem',
      marginBottom: '1.5rem',
      background: '#fff',
      boxSizing: 'border-box',
      fontSize: '1.1rem',
      fontFamily: 'inherit',
      height: '100%',
      display: 'flex',
      alignItems: 'stretch',
      justifyContent: 'center',
    }}>
      <div style={{ position: 'relative', width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Button
          data-testid="source-selector-btn"
          variant="outline-secondary"
          aria-haspopup="menu"
          aria-expanded={sourcePopupOpen}
          onClick={onButtonClick}
          style={{ minWidth: 180 }}
        >
          {`Source: ${selectedSource ? selectedSource.name : ''}`}
        </Button>
        {sourcePopupOpen && (
          <ul
            data-testid="source-selector-menu"
            role="menu"
            style={{
              position: 'absolute',
              left: '100%',
              top: 0,
              minWidth: 180,
              background: '#fff',
              border: '1px solid #ccc',
              boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
              zIndex: 100,
              padding: 0,
              margin: 0,
              listStyle: 'none',
            }}
          >
            {sources?.map((source) => (
              <li
                key={source.id}
                role="menuitem"
                aria-selected={sourceId === source.id}
                tabIndex={0}
                style={{
                  padding: '0.7rem 1.5rem',
                  background: hoveredSource === source.id ? '#f0f4fa' : '#fff',
                  cursor: 'pointer',
                  fontWeight: 500,
                  color: '#222',
                  border: 'none',
                  outline: 'none',
                  width: '100%',
                  textAlign: 'left',
                }}
                onMouseEnter={() => setHoveredSource(source.id)}
                onMouseLeave={() => setHoveredSource(null)}
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
