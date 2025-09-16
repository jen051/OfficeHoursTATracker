import { useEffect, useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'


// Element Functinos

export function Square() {
  return (
    <div className="square"></div>
  )
}

export function Card({ title, children, className = "" }) {
  return (
    <div className={`card ${className}`}>
      <h2>{title}</h2>
      <div className="card-content">{children}</div>
    </div>
  );
}

function App() {
  const [scans, setScans] = useState([])
  const [queue, setQueue] = useState([])

  useEffect(() => {
    console.log("Fetching scans from API...")
    const fetchScans = () => {
      fetch('/api/scans')
      .then(r => r.json())
      .then(d => {
      console.log("API response:", d);
      setScans(d);
      })
      .catch(() => setScans('API error'))
    }
    fetchScans();
    const interval = setInterval(fetchScans, 1000);
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    console.log("Fetching queue from API...")
    const fetchQueue = () => {
    fetch('/api/queue')
      .then(r => r.json())
      .then(d => {
      setQueue(d);
      })
      .catch(() => setQueue('API error'))
    }
    fetchQueue();
    const interval = setInterval(fetchQueue, 1000);
    return () => clearInterval(interval)
  }, [])

  return (
    <div>
      <div 
        style={{ display: "flex", alignItems: "center", gap: "10rem", marginBottom: "1rem" }}
      >
        <h1 className="left-header">
          CS2050 Office Hours
        </h1>

        <Card 
        title="How to Use the Queue"
        className="compact-card"> 
          <p>Scan your Buzzcard at the front table scanner. 
            It will record the last 4 digits of your Buzzcard and display them on the queue. 
            When a TA calls your number, scan again to remove yourself from the queue!</p>
        </Card>
      </div>
      <div>
        <div style={{ display: "flex", gap: "1rem", minHeight: "400px" }}>
          <Card 
          title="Present TAs"
          className="card">{scans.length === 0 ? (
          <p>No scans yet</p>
        ) : (
          <ul>
            {scans.map(scan => (
              <li key={scan.id}>
                {scan}
              </li>
            ))}
          </ul>
        )}
        </Card>
          <Card
          title="Queue"
          className="card">{queue.length === 0 ? (
          <p>No queue yet</p>
        ) : (
          <ul>
            {queue.map(queue_element => (
              <li key={queue_element.id}>
                {queue_element}
              </li>
            ))}
          </ul>
        )}</Card>
        
        
        </div>
      </div>
    </div>
  )
}


export default App
