import { useState, useEffect, useRef } from 'react';
import { Search, FileText, Upload, BarChart3, Settings, Moon, Sun, Download, Zap } from 'lucide-react';
import '../styles/clean.css';

interface Command {
  id: string;
  label: string;
  icon: React.ReactNode;
  shortcut?: string;
  action: () => void;
  category: string;
}

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  commands: Command[];
}

export default function CommandPalette({ isOpen, onClose, commands }: CommandPaletteProps) {
  const [search, setSearch] = useState('');
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const filteredCommands = commands.filter(cmd =>
    cmd.label.toLowerCase().includes(search.toLowerCase()) ||
    cmd.category.toLowerCase().includes(search.toLowerCase())
  );

  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
      setSearch('');
      setSelectedIndex(0);
    }
  }, [isOpen]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return;

      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex(prev => (prev + 1) % filteredCommands.length);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex(prev => (prev - 1 + filteredCommands.length) % filteredCommands.length);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        if (filteredCommands[selectedIndex]) {
          filteredCommands[selectedIndex].action();
          onClose();
        }
      } else if (e.key === 'Escape') {
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, filteredCommands, selectedIndex, onClose]);

  if (!isOpen) return null;

  return (
    <div className="clean-command-overlay" onClick={onClose}>
      <div className="clean-command-palette" onClick={(e) => e.stopPropagation()}>
        <input
          ref={inputRef}
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Type a command or search..."
          className="clean-command-input"
        />
        <div style={{ maxHeight: '400px', overflowY: 'auto' }} className="clean-scrollbar">
          {filteredCommands.length === 0 ? (
            <div style={{ padding: '32px', textAlign: 'center', color: 'var(--clean-text-tertiary)' }}>
              No commands found
            </div>
          ) : (
            filteredCommands.map((cmd, index) => (
              <div
                key={cmd.id}
                onClick={() => {
                  cmd.action();
                  onClose();
                }}
                className={`clean-command-item ${index === selectedIndex ? 'selected' : ''}`}
                onMouseEnter={() => setSelectedIndex(index)}
              >
                <div style={{ color: 'var(--clean-accent)' }}>
                  {cmd.icon}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ color: 'var(--clean-text-primary)', fontWeight: 500, fontSize: '14px' }}>
                    {cmd.label}
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--clean-text-tertiary)', marginTop: '2px' }}>
                    {cmd.category}
                  </div>
                </div>
                {cmd.shortcut && (
                  <div style={{
                    fontSize: '11px',
                    color: 'var(--clean-text-tertiary)',
                    background: 'var(--clean-bg-secondary)',
                    padding: '4px 8px',
                    borderRadius: '4px',
                    fontFamily: 'monospace'
                  }}>
                    {cmd.shortcut}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
        <div style={{
          padding: '12px 16px',
          borderTop: '1px solid var(--clean-border)',
          fontSize: '12px',
          color: 'var(--clean-text-tertiary)',
          display: 'flex',
          gap: '16px',
          background: 'var(--clean-bg-secondary)'
        }}>
          <span>↑↓ Navigate</span>
          <span>↵ Select</span>
          <span>Esc Close</span>
        </div>
      </div>
    </div>
  );
}
