import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import { LoadingSpinner, ErrorMessage } from '../components/common';
import './Register.css';

interface FormData {
  name: string;
  studentId: string;
  password: string;
  confirmPassword: string;
}

interface FormErrors {
  name?: string;
  studentId?: string;
  password?: string;
  confirmPassword?: string;
}

const Register: React.FC = () => {
  const { t } = useTranslation('auth');
  const [formData, setFormData] = useState<FormData>({
    name: '',
    studentId: '',
    password: '',
    confirmPassword: '',
  });
  const [formErrors, setFormErrors] = useState<FormErrors>({});

  const { register, isLoading, error, isAuthenticated, clearError } = useAuth();
  const navigate = useNavigate();

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  // Clear errors when component unmounts
  useEffect(() => {
    return () => clearError();
  }, [clearError]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear field error when user starts typing
    if (formErrors[name as keyof FormErrors]) {
      setFormErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  const validateForm = (): boolean => {
    const errors: FormErrors = {};

    if (!formData.name.trim()) {
      errors.name = t('register.errors.nameRequired');
    } else if (formData.name.trim().length < 2) {
      errors.name = t('register.errors.nameMinLength');
    }

    if (!formData.studentId.trim()) {
      errors.studentId = t('register.errors.studentIdRequired');
    } else if (!/^\d{10}$/.test(formData.studentId)) {
      errors.studentId = t('register.errors.invalidStudentId');
    }

    if (!formData.password) {
      errors.password = t('register.errors.passwordRequired');
    } else if (formData.password.length < 8) {
      errors.password = t('register.errors.passwordMinLength');
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(formData.password)) {
      errors.password = t('register.errors.passwordRequirements');
    }

    if (!formData.confirmPassword) {
      errors.confirmPassword = t('register.errors.confirmPasswordRequired');
    } else if (formData.password !== formData.confirmPassword) {
      errors.confirmPassword = t('register.errors.passwordMismatch');
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    try {
      await register({
        name: formData.name.trim(),
        student_id: formData.studentId.trim(),
        password: formData.password,
      });
      // Navigation will happen automatically via useEffect
    } catch (err) {
      // Error is handled by AuthContext
    }
  };

  return (
    <div className="register-page">
      <div className="register-container">
        <div className="register-header">
          <span className="register-logo">🎓</span>
          <h1>{t('register.title')}</h1>
          <p>{t('register.subtitle')}</p>
        </div>

        <form className="register-form" onSubmit={handleSubmit}>
          {error && <ErrorMessage message={error} />}

          <div className="form-group">
            <label htmlFor="name">{t('register.nameLabel')} *</label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder={t('register.namePlaceholder')}
              disabled={isLoading}
              className={formErrors.name ? 'error' : ''}
            />
            {formErrors.name && <span className="field-error">{formErrors.name}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="studentId">{t('register.studentIdLabel')} *</label>
            <input
              type="text"
              id="studentId"
              name="studentId"
              value={formData.studentId}
              onChange={handleChange}
              placeholder={t('register.studentIdPlaceholder')}
              disabled={isLoading}
              className={formErrors.studentId ? 'error' : ''}
              maxLength={10}
            />
            {formErrors.studentId && <span className="field-error">{formErrors.studentId}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="password">{t('register.passwordLabel')} *</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder={t('register.passwordPlaceholder')}
              disabled={isLoading}
              className={formErrors.password ? 'error' : ''}
            />
            {formErrors.password && <span className="field-error">{formErrors.password}</span>}
            <span className="field-hint">{t('register.passwordHint')}</span>
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword">{t('register.confirmPasswordLabel')} *</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder={t('register.confirmPasswordPlaceholder')}
              disabled={isLoading}
              className={formErrors.confirmPassword ? 'error' : ''}
            />
            {formErrors.confirmPassword && <span className="field-error">{formErrors.confirmPassword}</span>}
          </div>

          <button
            type="submit"
            className="register-button"
            disabled={isLoading}
          >
            {isLoading ? <LoadingSpinner size="small" message="" /> : t('register.submitButton')}
          </button>
        </form>

        <div className="register-footer">
          <p>
            {t('register.hasAccount')}{' '}
            <Link to="/login" className="login-link">
              {t('register.signIn')}
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Register;

