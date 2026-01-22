import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import { LoadingSpinner, ErrorMessage } from '../components/common';
import './Login.css';

interface LocationState {
  from?: { pathname: string };
}

const Login: React.FC = () => {
  const { t } = useTranslation('auth');
  const [studentId, setStudentId] = useState('');
  const [password, setPassword] = useState('');
  const [formErrors, setFormErrors] = useState<{ studentId?: string; password?: string }>({});

  const { login, isLoading, error, isAuthenticated, clearError } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const state = location.state as LocationState;
  const from = state?.from?.pathname || '/dashboard';

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate(from, { replace: true });
    }
  }, [isAuthenticated, navigate, from]);

  // Clear errors when component unmounts
  useEffect(() => {
    return () => clearError();
  }, [clearError]);

  const validateForm = (): boolean => {
    const errors: { studentId?: string; password?: string } = {};

    if (!studentId.trim()) {
      errors.studentId = t('login.errors.studentIdRequired');
    } else if (!/^\d{10}$/.test(studentId)) {
      errors.studentId = t('login.errors.invalidStudentId');
    }

    if (!password) {
      errors.password = t('login.errors.passwordRequired');
    } else if (password.length < 6) {
      errors.password = t('login.errors.passwordMinLength');
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    try {
      await login({ student_id: studentId, password });
      // Navigation will happen automatically via useEffect
    } catch (err) {
      // Error is handled by AuthContext
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <span className="login-logo">🎓</span>
          <h1>{t('login.title')}</h1>
          <p>{t('login.subtitle')}</p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          {error && <ErrorMessage message={error} />}

          <div className="form-group">
            <label htmlFor="studentId">{t('login.studentIdLabel')}</label>
            <input
              type="text"
              id="studentId"
              value={studentId}
              onChange={(e) => {
                setStudentId(e.target.value);
                if (formErrors.studentId) setFormErrors({ ...formErrors, studentId: undefined });
              }}
              placeholder={t('login.studentIdPlaceholder')}
              disabled={isLoading}
              className={formErrors.studentId ? 'error' : ''}
              maxLength={10}
            />
            {formErrors.studentId && <span className="field-error">{formErrors.studentId}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="password">{t('login.passwordLabel')}</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                if (formErrors.password) setFormErrors({ ...formErrors, password: undefined });
              }}
              placeholder={t('login.passwordPlaceholder')}
              disabled={isLoading}
              className={formErrors.password ? 'error' : ''}
            />
            {formErrors.password && <span className="field-error">{formErrors.password}</span>}
          </div>

          <button
            type="submit"
            className="login-button"
            disabled={isLoading}
          >
            {isLoading ? <LoadingSpinner size="small" message="" /> : t('login.submitButton')}
          </button>
        </form>

        <div className="login-footer">
          <p>
            {t('login.noAccount')}{' '}
            <Link to="/register" className="register-link">
              {t('login.createAccount')}
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Login;

