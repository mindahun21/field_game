import { useState, useEffect } from 'react';
import './App.css';
import TransferGroupOwnershipForm from './components/TransferGroupOwnershipForm';

/**
 * Main application component for the admin mini-app.
 * Handles updating user points and navigating to group ownership transfer.
 */
function App() {
  const [groupName, setGroupName] = useState('');
  const [points, setPoints] = useState('');
  const [operation, setOperation] = useState('update');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [userRole, setUserRole] = useState('');
  const [currentView, setCurrentView] = useState('updatePoints');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const role = params.get('role');
    const view = params.get('view');

    if (role) {
      setUserRole(role);
      if (role !== 'ADMIN' && operation === 'set') {
        setOperation('update');
      }
    }
    if (view) {
        setCurrentView(view);
    }
  }, [operation]);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (searchQuery.trim() === '') {
      setSearchResults([]);
      return;
    }

    const endpoint = `/api/search_groups?q=${searchQuery}`;
    const apiUrl = import.meta.env.VITE_API_BASE_URL;
    const url = `${apiUrl}${endpoint}`;

    try {
      const response = await fetch(url, {
        headers: {
          'X-User-Role': userRole,
        },
      });
      const data = await response.json();
      if (response.ok) {
        setSearchResults(data.users);
      } else {
        setSearchResults([]);
      }
    } catch (err) {
      setSearchResults([]);
    }
  };

  const handleResultClick = (name) => {
    setGroupName(name);
    setSearchResults([]);
    setSearchQuery('');
  };

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
    const apiUrl = import.meta.env.VITE_API_BASE_URL;
    const url = `${apiUrl}${endpoint}`;

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Role': userRole,
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
        <div>
          <form onSubmit={handleSearch}>
            <h2>Search for Group</h2>
            <div className="form-group">
              <label htmlFor="searchGroup">Group Name Search</label>
              <input
                type="text"
                id="searchGroup"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Enter group name to search"
              />
            </div>
            <button type="submit">Search</button>
          </form>
          {searchResults.length > 0 && (
            <div className="search-results">
              {searchResults.map((user) => (
                <div
                  key={user.group_name}
                  className="search-result-item"
                  onClick={() => handleResultClick(user.group_name)}
                >
                  <span>{user.username}</span> (<span>{user.group_name}</span>)
                </div>
              ))}
            </div>
          )}

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
        </div>
      )}

      {currentView === 'transferOwnership' && <TransferGroupOwnershipForm userRole={userRole} />}

      {message && <p className="success-message">{message}</p>}
      {error && <p className="error-message">{error}</p>}
    </div>
  );
}

export default App;