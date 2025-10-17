import { useEffect, useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

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
  const [confirmation, setConfirmation] = useState("");
  const [gtid, setGtid] = useState("")
  const [inQueue, setInQueue] = useState(false);
  const [hash, setHash] = useState(null);

  useEffect(() => {
    fetch("https://officehourstatracker.onrender.com/api/in-queue-status")
      .then(res => setInQueue(res.data.in_queue))
      .catch(err => console.error(err));
  }, []);

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
    if (data.random_name && data.random_name != -1) {
      setConfirmation(`You’ve been added to the queue as ${data.random_name}`);
    } else if (data.random_name == -1) {
      setConfirmation(`You’ve been removed from the queue`);
    }
  })
    .catch(err => console.error("Error:", err));

    setTimeout(() => setConfirmation(""), 3000);
    setGtid("");
  }

  const buttonSubmit = (e) => {
    e.preventDefault();

    if (!inQueue) {
      fetch("https://officehourstatracker.onrender.com/api/button-queue", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({})
      })
      .then(res => res.json())
      .then(data => {
        setInQueue(true);
        setHash(data.hash);
        if (data.random_name && data.random_name != -1) {
          setConfirmation(`You’ve been added to the queue as ${data.random_name}`);
        } else if (data.random_name == -1) {
          setConfirmation(`You’ve been removed from the queue`);
        }
    })
      .catch(err => console.error("Error:", err));

    } else {
        fetch("https://officehourstatracker.onrender.com/api/dequeue", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ hash })
      })
      .then(res => res.json())
      .then(data => {
        if (data.status === "success") {
          setInQueue(false);
          setHash(null);
          setConfirmation(`Dequeued ${data.removed_name}`);
        }
      })
      .catch(err => console.error(err));
    }
  }

  const [scans, setScans] = useState([])
  const [queue, setQueue] = useState([])

  useEffect(() => {
    //console.log("Fetching scans from API...")
    const fetchScans = () => {
      fetch('https://officehourstatracker.onrender.com/api/scans')
      .then(r => r.json())
      .then(d => {
      //console.log("API response:", d);
      setScans(d);
      })
      .catch(() => setScans('API error'))
    }
    fetchScans();
    const interval = setInterval(fetchScans, 1000);
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    //console.log("Fetching queue from API...")
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
        <h1 style={{ color: "#F2F4F3" }}>
          CS2050 Office Hours
        </h1>
        <p style={{ color: "#F2F4F3" }}>Students: Click the button to add yourself to the queue.</p>
        <p style={{ color: "#F2F4F3" }}>TAs: Input your GTID to sign in.</p>
      </div>
     
      <div>
        <div className='cards-row'>
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
        <div className="center-div">
          
            <form onSubmit={buttonSubmit} style={{ marginBottom: "1.5rem" }}>
              {confirmation && <p className="confirmation">{confirmation}</p>}
              <label htmlFor="gtid" style={{ color: "#F2F4F3" }}>Students: Press this button!</label>
              <div className="button-group">
                <button type="submit">
                  {inQueue ? "Dequeue" : "Enqueue"}
                </button>
              </div>
            </form>

            <form onSubmit={handleSubmit}>
              <label htmlFor="gtid" style={{ color: "#F2F4F3" }}>TAs: Input GTID Here:</label>
              <input id="gtid" name="gtid" autocomplete="off" value={gtid} onChange={e => setGtid(e.target.value)}/>
              <div className="button-group">
                <button type="reset" onClick={() => setGtid("")}>Reset</button>
                <button type="submit">Submit GTID</button>
              </div>
            </form>
          </div>
      </div>
    </div>
  )
}


export default App
