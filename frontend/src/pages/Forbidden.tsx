import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import './Forbidden.css';

const Forbidden: React.FC = () => {
  const { t } = useTranslation('common');
  const navigate = useNavigate();

  const handleGoBack = () => {
    navigate(-1); // 返回上一页
  };

  const handleGoHome = () => {
    navigate('/'); // 返回首页
  };

  return (
    <div className="forbidden-page">
      <div className="forbidden-content">
        <div className="forbidden-icon">🔒</div>
        <h1 className="forbidden-title">{t('forbidden.title', 'Access Denied')}</h1>
        <p className="forbidden-message">
          {t('forbidden.message', 'Sorry, you do not have permission to access this page.')}
        </p>
        <div className="forbidden-actions">
          <button className="btn btn-primary" onClick={handleGoBack}>
            {t('forbidden.goBack', 'Go Back')}
          </button>
          <button className="btn btn-secondary" onClick={handleGoHome}>
            {t('forbidden.goHome', 'Go Home')}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Forbidden;