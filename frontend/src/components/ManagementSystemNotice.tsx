/**
 * 管理系统引导组件
 * 
 * 用于提示教师使用外部管理系统创建和管理作业
 */
import React from 'react';
import './ManagementSystemNotice.css';

interface ManagementSystemNoticeProps {
  /** 管理系统的访问路径或URL */
  managementSystemPath?: string;
  /** 是否显示为横幅样式 */
  variant?: 'banner' | 'card';
  /** 是否可关闭 */
  dismissible?: boolean;
}

export const ManagementSystemNotice: React.FC<ManagementSystemNoticeProps> = ({
  managementSystemPath = 'E:\\Code\\repo\\管理系统',
  variant = 'banner',
  dismissible = false,
}) => {
  const [dismissed, setDismissed] = React.useState(false);

  if (dismissed) {
    return null;
  }

  return (
    <div className={`management-notice management-notice--${variant}`}>
      <div className="management-notice__icon">
        📢
      </div>
      <div className="management-notice__content">
        <h3 className="management-notice__title">
          作业管理功能已迁移
        </h3>
        <p className="management-notice__message">
          作业的创建、编辑和删除功能现已迁移至<strong>作业管理系统</strong>。
          本系统专注于为学生提供作业提交、AI评分、查重检测等学习支持功能。
        </p>
        <div className="management-notice__actions">
          <div className="management-notice__path">
            <span className="management-notice__path-label">管理系统路径：</span>
            <code className="management-notice__path-value">{managementSystemPath}</code>
          </div>
          <div className="management-notice__features">
            <span className="management-notice__features-label">您仍可在本系统中：</span>
            <ul className="management-notice__features-list">
              <li>✅ 查看所有作业和统计数据</li>
              <li>✅ 查看学生提交记录</li>
              <li>✅ 进行AI评分和手动评分</li>
              <li>✅ 使用查重检测功能</li>
              <li>✅ 查看代码分析报告</li>
            </ul>
          </div>
        </div>
      </div>
      {dismissible && (
        <button
          className="management-notice__close"
          onClick={() => setDismissed(true)}
          aria-label="关闭提示"
        >
          ×
        </button>
      )}
    </div>
  );
};

export default ManagementSystemNotice;

