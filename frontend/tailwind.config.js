/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        portal: {
          bg: '#F7F8FA',
          card: '#FFFFFF',
          sidebar: '#F1F3F7',
          border: '#D8DEE8',
          borderLight: '#E8ECF2',
          navy: '#0F2744',
          navyLight: '#1B3A6B',
          navyHover: '#142C52',
          text: '#1E293B',
          textMuted: '#64748B',
          textLight: '#94A3B8',
          saffron: '#D97706',
          green: '#15803D',
          
          // Status tokens (desaturated for official authority)
          statusCorroborated: '#0D8253',
          statusCorroboratedBg: '#EDF9F2',
          statusCorroboratedBorder: '#A3E6C3',
          
          statusContradicted: '#C53030',
          statusContradictedBg: '#FDF2F2',
          statusContradictedBorder: '#F8B4B4',
          
          statusUnverified: '#B45309',
          statusUnverifiedBg: '#FFFBEB',
          statusUnverifiedBorder: '#FDE68A',
        }
      },
      fontFamily: {
        serif: ['"Merriweather"', '"Source Serif 4"', 'Georgia', 'serif'],
        sans: ['"Inter"', '"IBM Plex Sans"', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"Fira Code"', 'monospace'],
      },
      boxShadow: {
        'portal-card': '0 1px 3px 0 rgba(15, 39, 68, 0.06), 0 1px 2px -1px rgba(15, 39, 68, 0.04)',
        'portal-elevated': '0 4px 6px -1px rgba(15, 39, 68, 0.08), 0 2px 4px -2px rgba(15, 39, 68, 0.04)',
      },
      borderRadius: {
        'portal': '4px',
      }
    },
  },
  plugins: [],
}
