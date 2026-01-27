// 简单测试以验证Jest配置
test('simple test should pass', () => {
  expect(1).toBe(1);
});

// 测试一个简单的工具函数
describe('Simple utility tests', () => {
  test('should correctly add two numbers', () => {
    const add = (a, b) => a + b;
    expect(add(2, 3)).toBe(5);
  });
});
