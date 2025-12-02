import React, { useState } from 'react';

/**
 * Component for transferring ownership of a game group.
 * Allows ADMIN users to assign an existing group to a new owner.
 *
 * @param {object} props - Component props.
 * @param {string} props.userRole - The role of the current user (e.g., "ADMIN", "GAME_ADMIN").
 */
function TransferGroupOwnershipForm({ userRole }) {
  const [currentGroupName, setCurrentGroupName] = useState('');
  const [newOwnerUsername, setNewOwnerUsername] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  /**
   * Handles the submission of the transfer ownership form.
   * Sends a request to the API to transfer group ownership.
   *
   * @param {Event} e - The form submission event.
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');

    if (!currentGroupName || !newOwnerUsername) {
      setError('Both fields are required.');
      return;
    }

    if (userRole !== 'ADMIN') {
      setError('You are not authorized to transfer group ownership.');
      return;
    }

    const endpoint = '/api/transfer_group_ownership';
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
          current_group_name: currentGroupName,
          new_owner_username: newOwnerUsername,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Something went wrong');
      }

      setMessage(data.message);
      setCurrentGroupName('');
      setNewOwnerUsername('');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="transfer-group-form">
      <h3>Transfer Group Ownership</h3>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="currentGroupName">Current Group Name</label>
          <input
            type="text"
            id="currentGroupName"
            value={currentGroupName}
            onChange={(e) => setCurrentGroupName(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="newOwnerUsername">
            New Owner Username (@username)
          </label>
          <input
            type="text"
            id="newOwnerUsername"
            value={newOwnerUsername}
            onChange={(e) => setNewOwnerUsername(e.target.value)}
            required
          />
        </div>
        <button type="submit" disabled={userRole !== 'ADMIN'}>
          Transfer Ownership
        </button>
      </form>
      {message && <p className="success-message">{message}</p>}
      {error && <p className="error-message">{error}</p>}
      {userRole !== 'ADMIN' && (
        <p className="info-message">
          Only Super Admins can transfer group ownership.
        </p>
      )}
    </div>
  );
}

export default TransferGroupOwnershipForm;
