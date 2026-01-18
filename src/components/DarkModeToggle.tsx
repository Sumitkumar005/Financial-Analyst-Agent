import { Moon, Sun } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function DarkModeToggle() {
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    // Check localStorage or default to dark
    const saved = localStorage.getItem('darkMode');
    if (saved !== null) {
      setIsDark(saved === 'true');
    }
    applyTheme(isDark);
  }, []);

  const applyTheme = (dark: boolean) => {
    if (dark) {
      document.documentElement.style.setProperty('--premium-bg-primary', '#0a0e27');
      document.documentElement.style.setProperty('--premium-bg-secondary', '#131829');
      document.documentElement.style.setProperty('--premium-text-primary', '#f8fafc');
    } else {
      document.documentElement.style.setProperty('--premium-bg-primary', '#ffffff');
      document.documentElement.style.setProperty('--premium-bg-secondary', '#f8f9fa');
      document.documentElement.style.setProperty('--premium-text-primary', '#1a1a1a');
    }
  };

  const toggle = () => {
    const newMode = !isDark;
    setIsDark(newMode);
    localStorage.setItem('darkMode', newMode.toString());
    applyTheme(newMode);
  };

  return (
    <button
      onClick={toggle}
      className="premium-button"
      style={{
        width: '44px',
        height: '44px',
        padding: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        borderRadius: '10px'
      }}
      title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
    >
      {isDark ? <Sun size={20} /> : <Moon size={20} />}
    </button>
  );
}
