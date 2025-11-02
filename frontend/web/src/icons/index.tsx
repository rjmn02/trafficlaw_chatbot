export function IconCopy(props: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className={props.className || "w-4 h-4"}>
      <path d="M6 4a2 2 0 012-2h5a2 2 0 012 2v6a2 2 0 01-2 2H8a2 2 0 01-2-2V4z"/>
      <path d="M4 6a2 2 0 00-2 2v6a2 2 0 002 2h6a2 2 0 002-2v-1H8a4 4 0 01-4-4V6z"/>
    </svg>
  );
}

export function IconRefresh(props: { className?: string }) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={props.className || "w-4 h-4"}>
      <path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0118.8-4.3M22 12.5a10 10 0 01-18.8 4.2" />
    </svg>
  );
}

