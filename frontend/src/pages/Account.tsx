import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import { LoadingSpinner, ErrorMessage } from '../components/common';
import './Account.css';

const Account: React.FC = () => {
  const { t } = useTranslation('auth');
  const navigate = useNavigate();
  const { user, logout, updateProfile, uploadAvatar, deleteAccount, changePassword, error, clearError } = useAuth();
  
  const [isEditingName, setIsEditingName] = useState(false);
  const [newName, setNewName] = useState(user?.name || '');
  const [isUploadingAvatar, setIsUploadingAvatar] = useState(false);
  const [isChangingPassword, setIsChangingPassword] = useState(false);
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isDeletingAccount, setIsDeletingAccount] = useState(false);
  const [deletePassword, setDeletePassword] = useState('');
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState('');
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpdateName = async () => {
    if (!newName.trim()) return;
    setIsLoading(true);
    try {
      await updateProfile(newName.trim());
      setIsEditingName(false);
      setSuccessMessage(t('account.nameUpdated'));
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      // Error handled by AuthContext
    } finally {
      setIsLoading(false);
    }
  };

  const handleAvatarClick = () => {
    fileInputRef.current?.click();
  };

  const handleAvatarChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    setIsUploadingAvatar(true);
    try {
      await uploadAvatar(file);
      setSuccessMessage(t('account.avatarUpdated'));
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      // Error handled by AuthContext
    } finally {
      setIsUploadingAvatar(false);
    }
  };

  const handleChangePassword = async () => {
    if (newPassword !== confirmPassword) {
      return;
    }
    setIsLoading(true);
    try {
      await changePassword(oldPassword, newPassword);
      // 密码修改成功后会自动登出
    } catch (err) {
      // Error handled by AuthContext
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    setIsDeletingAccount(true);
    try {
      await deleteAccount(deletePassword);
      navigate('/login');
    } catch (err) {
      // Error handled by AuthContext
    } finally {
      setIsDeletingAccount(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const getAvatarUrl = () => {
    if (user?.avatar_url) {
      // 如果是相对路径，添加后端 URL
      if (user.avatar_url.startsWith('/')) {
        return `http://localhost:8000${user.avatar_url}`;
      }
      return user.avatar_url;
    }
    return null;
  };

  return (
    <div className="account-page">
      <div className="account-container">
        <h1 className="account-title">{t('account.title')}</h1>
        
        {error && <ErrorMessage message={error} onDismiss={clearError} />}
        {successMessage && <div className="success-message">{successMessage}</div>}

        {/* 个人资料卡片 */}
        <div className="account-card">
          <h2 className="card-title">{`👤 ${t('account.profile')}`}</h2>
          
          <div className="profile-section">
            <div className="avatar-section">
              <div className="avatar-container" onClick={handleAvatarClick}>
                {getAvatarUrl() ? (
                  <img src={getAvatarUrl()!} alt="Avatar" className="avatar-image" />
                ) : (
                  <div className="avatar-placeholder">
                    {user?.name?.charAt(0) || user?.student_id?.charAt(0) || '?'}
                  </div>
                )}
                <div className="avatar-overlay">
                  {isUploadingAvatar ? <LoadingSpinner size="small" /> : '📷'}
                </div>
              </div>
              <input
                type="file"
                ref={fileInputRef}
                onChange={handleAvatarChange}
                accept="image/jpeg,image/png,image/gif,image/webp"
                style={{ display: 'none' }}
              />
              <p className="avatar-hint">{t('account.clickToUpload')}</p>
            </div>

            <div className="info-section">
              <div className="info-row">
                <span className="info-label">{t('account.studentId')}:</span>
                <span className="info-value readonly">{user?.student_id}</span>
              </div>

              <div className="info-row">
                <span className="info-label">{t('account.name')}:</span>
                {isEditingName ? (
                  <div className="edit-name-form">
                    <input
                      type="text"
                      value={newName}
                      onChange={(e) => setNewName(e.target.value)}
                      className="name-input"
                      placeholder={t('account.enterName')}
                    />
                    <button onClick={handleUpdateName} disabled={isLoading} className="btn-save">
                      {isLoading ? <LoadingSpinner size="small" /> : t('account.save')}
                    </button>
                    <button onClick={() => setIsEditingName(false)} className="btn-cancel">
                      {t('account.cancel')}
                    </button>
                  </div>
                ) : (
                  <div className="name-display">
                    <span className="info-value">{user?.name || t('account.notSet')}</span>
                    <button onClick={() => setIsEditingName(true)} className="btn-edit">
                      ✏️ {t('account.edit')}
                    </button>
                  </div>
                )}
              </div>

              <div className="info-row">
                <span className="info-label">{t('account.role')}:</span>
                <span className="info-value">{user?.role}</span>
              </div>

              <div className="info-row">
                <span className="info-label">{t('account.lastLogin')}:</span>
                <span className="info-value">
                  {user?.last_login ? new Date(user.last_login).toLocaleString() : t('account.never')}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* 安全设置卡片 */}
        <div className="account-card">
          <h2 className="card-title">{`🔒 ${t('account.security')}`}</h2>

          {!isChangingPassword ? (
            <button onClick={() => setIsChangingPassword(true)} className="btn-secondary">
              {t('account.changePassword')}
            </button>
          ) : (
            <div className="password-form">
              <div className="form-group">
                <label>{t('account.oldPassword')}</label>
                <input
                  type="password"
                  value={oldPassword}
                  onChange={(e) => setOldPassword(e.target.value)}
                  placeholder={t('account.enterOldPassword')}
                />
              </div>
              <div className="form-group">
                <label>{t('account.newPassword')}</label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder={t('account.enterNewPassword')}
                />
              </div>
              <div className="form-group">
                <label>{t('account.confirmPassword')}</label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder={t('account.confirmNewPassword')}
                />
              </div>
              <div className="form-actions">
                <button onClick={handleChangePassword} disabled={isLoading} className="btn-primary">
                  {isLoading ? <LoadingSpinner size="small" /> : t('account.updatePassword')}
                </button>
                <button onClick={() => setIsChangingPassword(false)} className="btn-cancel">
                  {t('account.cancel')}
                </button>
              </div>
            </div>
          )}
        </div>

        {/* 账户操作卡片 */}
        <div className="account-card">
          <h2 className="card-title">{`⚙️ ${t('account.actions')}`}</h2>

          <button onClick={handleLogout} className="btn-secondary logout-btn">
            🚪 {t('logout')}
          </button>

          <div className="danger-zone">
            <h3>{t('account.dangerZone')}</h3>
            {!showDeleteConfirm ? (
              <button onClick={() => setShowDeleteConfirm(true)} className="btn-danger">
                🗑️ {t('account.deleteAccount')}
              </button>
            ) : (
              <div className="delete-confirm">
                <p className="warning-text">{t('account.deleteWarning')}</p>
                <div className="form-group">
                  <label>{t('account.confirmPassword')}</label>
                  <input
                    type="password"
                    value={deletePassword}
                    onChange={(e) => setDeletePassword(e.target.value)}
                    placeholder={t('account.enterPasswordToConfirm')}
                  />
                </div>
                <div className="form-actions">
                  <button
                    onClick={handleDeleteAccount}
                    disabled={isDeletingAccount || !deletePassword}
                    className="btn-danger"
                  >
                    {isDeletingAccount ? <LoadingSpinner size="small" /> : t('account.confirmDelete')}
                  </button>
                  <button onClick={() => setShowDeleteConfirm(false)} className="btn-cancel">
                    {t('account.cancel')}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Account;

