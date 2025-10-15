import { useEffect, useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'


const [confirmation, setConfirmation] = useState("");

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
  const handleSubmit = (e) => {
    e.preventDefault();

    console.log("submitted")

    const form = e.target;
    const formData = new FormData(form);

    const formJson = Object.fromEntries(formData.entries());

    

    fetch("https://officehourstatracker.onrender.com/api/manual-scan", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(formJson)
    })
    .then(res => res.json())
    .then(data => {
    if (data.random_name) {
      setConfirmation(`You’ve been added to the queue as ${data.random_name}`);
    }})
    .catch(err => console.error("Error:", err));

    setTimeout(() => setConfirmation(""), 3000);
  }

  const [scans, setScans] = useState([])
  const [queue, setQueue] = useState([])

  useEffect(() => {
    console.log("Fetching scans from API...")
    const fetchScans = () => {
      fetch('https://officehourstatracker.onrender.com/api/scans')
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
    fetch('https://officehourstatracker.onrender.com/api/queue')
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
        style={{textAlign: "center", alignItems: "center", gap: "2rem", marginBottom: "0.25rem", marginTop: 0 }}
      >
        <h1>
          CS2050 Office Hours
        </h1>
        <p>Input your GTID in the text box and it will map you to an anonymous name.
            When a TA calls your name, reenter your GTID to dequeue yourself!</p>
      </div>
     
      <div>
        <div style={{ display: "flex", gap: "1rem", minHeight: "400px" }}>
          <Card 
          title="Present TAs"
          style={{ flex: 1 }}
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
          style={{ flex: 1 }}
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
        <div className="center-div">
            <form onSubmit={handleSubmit}>
              <label htmlFor="gtid">Input GTID Here:</label>
              <input id="gtid" name="gtid" />

              <div className="button-group">
                <button type="reset">Reset</button>
                <button type="submit">Submit GTID</button>
              </div>
              {confirmation && <p className="confirmation">{confirmation}</p>}
            </form>
          </div>
      </div>
    </div>
  )
}


export default App
