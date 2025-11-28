import { useState, useEffect } from 'react';
import './App.css';
import TransferGroupOwnershipForm from './components/TransferGroupOwnershipForm'; // Import the new component

function App() {
  const [groupName, setGroupName] = useState('');
  const [points, setPoints] = useState('');
  const [operation, setOperation] = useState('update'); // 'update' or 'set'
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [userRole, setUserRole] = useState(''); // State to store the user's role
  const [currentView, setCurrentView] = useState('updatePoints'); // 'updatePoints' or 'transferOwnership'

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const role = params.get('role');
    if (role) {
      setUserRole(role);
      if (role !== 'ADMIN' && operation === 'set') {
        setOperation('update');
      }
    }
  }, [operation]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');

    if (!groupName || !points) {
      setError('All fields are required.');
      return;
    }

    if (userRole !== 'ADMIN' && operation === 'set') {
      setError('Only Super Admins can set (overwrite) points.');
      return;
    }

    const endpoint = operation === 'update' ? '/api/update_point' : '/api/set_point';
    const url = `http://127.0.0.1:8000${endpoint}`;

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Role': userRole, // Pass the user's role for API-side validation
        },
        body: JSON.stringify({
          group_name: groupName,
          points: parseInt(points, 10),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Something went wrong');
      }

      setMessage(`Success! Group ${data.group_name} now has ${data.point} points.`);
      setGroupName('');
      setPoints('');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="App">
      <h1>Admin Dashboard</h1>
      {userRole && <p>Your role: <strong>{userRole}</strong></p>}

      {userRole === 'ADMIN' && (
        <div className="admin-navigation">
          <button onClick={() => setCurrentView('updatePoints')} className={currentView === 'updatePoints' ? 'active' : ''}>
            Update Points
          </button>
          <button onClick={() => setCurrentView('transferOwnership')} className={currentView === 'transferOwnership' ? 'active' : ''}>
            Transfer Group Ownership
          </button>
        </div>
      )}

      {currentView === 'updatePoints' && (
        <form onSubmit={handleSubmit}>
          <h2>Update Group Points</h2>
          <div className="form-group">
            <label htmlFor="groupName">Group Name</label>
            <input
              type="text"
              id="groupName"
              value={groupName}
              onChange={(e) => setGroupName(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="points">Points</label>
            <input
              type="number"
              id="points"
              value={points}
              onChange={(e) => setPoints(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label htmlFor="operation">Operation</label>
            <select id="operation" value={operation} onChange={(e) => setOperation(e.target.value)}>
              <option value="update">Update (Add Points)</option>
              {userRole === 'ADMIN' && <option value="set">Set (Overwrite Points)</option>}
            </select>
          </div>
          <button type="submit">Submit</button>
        </form>
      )}

      {currentView === 'transferOwnership' && <TransferGroupOwnershipForm userRole={userRole} />}

      {message && <p className="success-message">{message}</p>}
      {error && <p className="error-message">{error}</p>}
    </div>
  );
}

export default App;