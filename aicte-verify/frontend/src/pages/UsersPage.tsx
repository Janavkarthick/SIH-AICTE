import React, { useEffect, useState } from 'react';
import { User, UserRole } from '../types';
import { authApi } from '../api/auth';
import AdvisoryBadge from '../components/AdvisoryBadge';

export const UsersPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // New user form modal
  const [showAddModal, setShowAddModal] = useState(false);
  const [newUsername, setNewUsername] = useState('');
  const [newFullName, setNewFullName] = useState('');
  const [newEmail, setNewEmail] = useState('');
  const [newRole, setNewRole] = useState<UserRole>('officer');
  const [newInstitution, setNewInstitution] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchUsers = async () => {
    setIsLoading(true);
    try {
      const data = await authApi.getUsers();
      setUsers(data);
    } catch (err) {
      console.error('Failed to load users', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const handleRoleChange = async (userId: string, role: UserRole) => {
    try {
      const updated = await authApi.updateUserRole(userId, role);
      setUsers((prev) => prev.map((u) => (u.id === userId ? updated : u)));
    } catch (err) {
      console.error('Role update failed', err);
    }
  };

  const handleAddUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    try {
      const created = await authApi.register({
        username: newUsername,
        full_name: newFullName,
        email: newEmail,
        role: newRole,
        institution_name: newInstitution,
      });
      setUsers((prev) => [...prev, created]);
      setShowAddModal(false);
      setNewUsername('');
      setNewFullName('');
      setNewEmail('');
      setNewInstitution('');
    } catch (err) {
      console.error('Add user failed', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const getRoleBadge = (role: UserRole) => {
    switch (role) {
      case 'officer':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'scrutiny_admin':
        return 'bg-purple-100 text-purple-800 border-purple-300';
      case 'admin':
        return 'bg-rose-100 text-rose-800 border-rose-300 font-bold';
      case 'college_user':
        return 'bg-emerald-100 text-emerald-800 border-emerald-300';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-extrabold text-slate-900">
            AICTE User & Access Control Management
          </h2>
          <p className="text-xs text-slate-500 mt-0.5">
            Admin console for managing scrutiny officers, scrutiny committee chairs, and college institutional representatives
          </p>
        </div>
        <div className="flex items-center gap-3">
          <AdvisoryBadge size="md" />
          <button
            type="button"
            onClick={() => setShowAddModal(true)}
            className="px-4 py-2 bg-aicte-600 hover:bg-aicte-700 text-white rounded-lg text-xs font-semibold shadow-sm transition"
          >
            + Add Authorized User
          </button>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
          <span className="text-xs font-bold uppercase text-slate-700 tracking-wider">
            Registered Stakeholders ({users.length})
          </span>
          <span className="text-xs text-slate-500">Role-Based Access Control (RBAC) Active</span>
        </div>

        {isLoading ? (
          <div className="py-16 text-center">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-aicte-600 border-t-transparent" />
            <p className="mt-2 text-xs text-slate-500 font-semibold">Loading Users...</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-100 text-slate-700 font-semibold uppercase text-[11px]">
                  <th className="py-3 px-4">Full Name</th>
                  <th className="py-3 px-4">Username & Email</th>
                  <th className="py-3 px-4">Institutional Affiliation</th>
                  <th className="py-3 px-4">Current Role</th>
                  <th className="py-3 px-4">Assign Role</th>
                  <th className="py-3 px-4 text-right">Created At</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {users.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-50 transition">
                    <td className="py-3.5 px-4 font-bold text-slate-900">{u.full_name}</td>
                    <td className="py-3.5 px-4 font-mono text-slate-600">
                      <div>{u.username}</div>
                      <div className="text-[11px] text-slate-400 font-sans">{u.email}</div>
                    </td>
                    <td className="py-3.5 px-4 text-slate-700 max-w-xs truncate">
                      {u.institution_name || 'AICTE Headquarters'}
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`inline-block px-2.5 py-0.5 rounded-full text-[11px] uppercase font-semibold border ${getRoleBadge(
                          u.role
                        )}`}
                      >
                        {u.role.replace('_', ' ')}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <select
                        value={u.role}
                        onChange={(e) => handleRoleChange(u.id, e.target.value as UserRole)}
                        className="text-xs border border-slate-300 rounded p-1 bg-white outline-none"
                      >
                        <option value="officer">Regional Officer</option>
                        <option value="scrutiny_admin">Scrutiny Admin</option>
                        <option value="college_user">College User</option>
                        <option value="admin">Tech Admin</option>
                      </select>
                    </td>
                    <td className="py-3.5 px-4 text-right text-slate-400 font-mono text-[11px]">
                      {new Date(u.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Add User Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full border border-slate-200 overflow-hidden">
            <div className="px-6 py-4 border-b border-slate-200 bg-slate-50 flex items-center justify-between">
              <h3 className="text-base font-bold text-slate-900">Add New Stakeholder Account</h3>
              <button
                type="button"
                onClick={() => setShowAddModal(false)}
                className="text-slate-400 hover:text-slate-600 text-xl font-bold p-1"
              >
                ×
              </button>
            </div>

            <form onSubmit={handleAddUser} className="p-6 space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  Full Legal Name
                </label>
                <input
                  type="text"
                  required
                  value={newFullName}
                  onChange={(e) => setNewFullName(e.target.value)}
                  placeholder="e.g. Dr. Ramesh Kumar"
                  className="w-full text-xs p-2.5 border border-slate-300 rounded-lg outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  Username
                </label>
                <input
                  type="text"
                  required
                  value={newUsername}
                  onChange={(e) => setNewUsername(e.target.value)}
                  placeholder="e.g. officer_ramesh"
                  className="w-full text-xs p-2.5 border border-slate-300 rounded-lg outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  Official Email
                </label>
                <input
                  type="email"
                  required
                  value={newEmail}
                  onChange={(e) => setNewEmail(e.target.value)}
                  placeholder="e.g. ramesh@aicte-india.org"
                  className="w-full text-xs p-2.5 border border-slate-300 rounded-lg outline-none"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  Assigned Role
                </label>
                <select
                  value={newRole}
                  onChange={(e) => setNewRole(e.target.value as UserRole)}
                  className="w-full text-xs p-2.5 border border-slate-300 rounded-lg bg-white outline-none"
                >
                  <option value="officer">Regional Officer</option>
                  <option value="scrutiny_admin">Scrutiny Admin</option>
                  <option value="college_user">College Representative</option>
                  <option value="admin">System Admin</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase mb-1">
                  Institution / Regional Office
                </label>
                <input
                  type="text"
                  value={newInstitution}
                  onChange={(e) => setNewInstitution(e.target.value)}
                  placeholder="e.g. AICTE Southern Regional Office, Chennai"
                  className="w-full text-xs p-2.5 border border-slate-300 rounded-lg outline-none"
                />
              </div>

              <div className="pt-3 border-t border-slate-200 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="px-4 py-2 text-xs font-semibold text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-lg"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 text-xs font-semibold text-white bg-aicte-600 hover:bg-aicte-700 rounded-lg shadow-sm"
                >
                  {isSubmitting ? 'Registering...' : 'Create Account'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default UsersPage;
