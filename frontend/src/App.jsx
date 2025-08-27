import { useEffect, useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [scans, setMsg] = useState([])

  useEffect(() => {
    console.log("Fetching scans from API...")
    fetch('/api/scans')
      .then(r => r.json())
      .then(d => {
      console.log("API response:", d);
      setMsg(d);
      })
      .catch(() => setMsg('API error'))
  }, [])

  return (
    <div>
      <h1>Recent Scans</h1>
      {scans.length === 0 ? (
        <p>No scans yet</p>
      ) : (
        <ul>
          {scans.map(scan => (
            <li key={scan.id}>
              {scan.gtid} — {scan.timestamp}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}


export default App
