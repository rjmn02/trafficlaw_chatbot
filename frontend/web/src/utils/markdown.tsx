import React from 'react';
import { COLORS } from '../constants';

// Render plain text with clickable safe links (no HTML execution)
function renderLinks(text: string) {
  const parts = text.split(/(https?:\/\/[^\s]+)/g);
  return parts.map((part, idx) => {
    if (/^https?:\/\//.test(part)) {
      return (
        <a 
          key={idx} 
          href={part} 
          target="_blank" 
          rel="noopener noreferrer" 
          className="underline break-words font-medium" 
          style={{ color: COLORS.accent }}
          onMouseEnter={(e) => { e.currentTarget.style.color = COLORS.primary; }}
          onMouseLeave={(e) => { e.currentTarget.style.color = COLORS.accent; }}
        >
          {part}
        </a>
      );
    }
    return <span key={idx}>{part}</span>;
  });
}

// Simple markdown-ish renderer supporting lists, code blocks, bold/italic, and links via renderLinks
export function renderMarkdown(text: string): React.ReactNode {
  const lines = text.split(/\r?\n/);
  const elements: React.ReactNode[] = [];
  let listItems: string[] = [];
  let inCode = false;
  let codeLines: string[] = [];
  
  const flushList = () => {
    if (listItems.length > 0) {
      elements.push(
        <ul className="list-disc pl-6 space-y-1" key={`ul-${elements.length}`}>
          {listItems.map((li, i) => <li key={i}>{renderInline(li)}</li>)}
        </ul>
      );
      listItems = [];
    }
  };
  
  const flushCode = () => {
    if (codeLines.length > 0) {
      elements.push(
        <pre key={`pre-${elements.length}`} className="rounded-lg p-4 overflow-x-auto shadow-sm border my-3" style={{ backgroundColor: '#f5f5f5', borderColor: COLORS.accent }}>
          <code className="text-sm" style={{ color: COLORS.dark, fontFamily: 'monospace' }}>{codeLines.join('\n')}</code>
        </pre>
      );
      codeLines = [];
    }
  };
  
  function renderInline(s: string) {
    // bold **text**, italic *text*, inline code `code`, blockquote > text
    const parts = s.split(/(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)/g);
    return parts.map((p, i) => {
      if (p.startsWith('**') && p.endsWith('**')) return <strong key={i} className="font-semibold">{p.slice(2, -2)}</strong>;
      if (p.startsWith('`') && p.endsWith('`')) return <code key={i} className="px-1.5 py-0.5 rounded text-sm font-mono" style={{ backgroundColor: '#f5f5f5', color: COLORS.dark }}>{p.slice(1, -1)}</code>;
      if (p.startsWith('*') && p.endsWith('*')) return <em key={i} className="italic">{p.slice(1, -1)}</em>;
      return <span key={i}>{renderLinks(p)}</span>;
    });
  }
  
  for (const line of lines) {
    if (line.trim().startsWith('```')) {
      if (inCode) { inCode = false; flushCode(); } else { inCode = true; }
      continue;
    }
    if (inCode) { codeLines.push(line); continue; }
    if (/^\s*[-*]\s+/.test(line)) { listItems.push(line.replace(/^\s*[-*]\s+/, '')); continue; }
    if (/^\s*>\s+/.test(line)) {
      flushList();
      const quoteText = line.replace(/^\s*>\s+/, '');
      elements.push(
        <blockquote 
          key={`blockquote-${elements.length}`} 
          className="border-l-4 pl-4 my-2 italic"
          style={{ borderColor: COLORS.accent, color: COLORS.dark, opacity: 0.8 }}
        >
          {renderInline(quoteText)}
        </blockquote>
      );
      continue;
    }
    // Simple table detection (basic markdown table)
    if (/^\s*\|/.test(line) && line.includes('|')) {
      flushList();
      const cells = line.split('|').map(c => c.trim()).filter(c => c);
      if (cells.length > 1) {
        elements.push(
          <div key={`table-${elements.length}`} className="overflow-x-auto my-2">
            <table className="min-w-full border-collapse">
              <tbody>
                <tr>
                  {cells.map((cell, i) => (
                    <td 
                      key={i} 
                      className="border px-3 py-2 text-sm"
                      style={{ borderColor: COLORS.accent }}
                    >
                      {renderInline(cell)}
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>
        );
      }
      continue;
    }
    flushList();
    if (line.trim() === '') { elements.push(<div key={`br-${elements.length}`} className="h-2" />); continue; }
    elements.push(<p key={`p-${elements.length}`} className="mb-2">{renderInline(line)}</p>);
  }
  flushList(); flushCode();
  return elements;
}

