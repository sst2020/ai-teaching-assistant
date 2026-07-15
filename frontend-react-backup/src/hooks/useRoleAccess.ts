import { useAuth } from '../contexts/AuthContext';

/**
 * 自定义Hook：检查用户角色权限
 * @param requiredRoles 需要的角色列表
 * @returns boolean 是否有权限
 */
export const useRoleAccess = (requiredRoles: string[]): boolean => {
  const { user } = useAuth();
  
  // 如果没有用户信息，则认为没有权限
  if (!user || !user.role) {
    return false;
  }

  // 检查用户角色是否在允许的角色列表中
  return requiredRoles.includes(user.role);
};

/**
 * 检查是否为学生角色
 */
export const useIsStudent = (): boolean => {
  return useRoleAccess(['student']);
};

/**
 * 检查是否为教师角色
 */
export const useIsTeacher = (): boolean => {
  return useRoleAccess(['teacher']);
};

/**
 * 检查是否为管理员角色
 */
export const useIsAdmin = (): boolean => {
  return useRoleAccess(['admin']);
};

/**
 * 检查是否为教师或管理员角色
 */
export const useIsTeacherOrAdmin = (): boolean => {
  return useRoleAccess(['teacher', 'admin']);
};