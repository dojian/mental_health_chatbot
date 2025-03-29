export const useRouter = () => ({
  push: jest.fn(),
  replace: jest.fn(),
  refresh: jest.fn(),
  back: jest.fn(),
  forward: jest.fn(),
});

// Add a dummy test to prevent the empty test suite error
describe('navigation mock', () => {
  it('provides mock router functions', () => {
    const router = useRouter();
    expect(router.push).toBeDefined();
    expect(router.replace).toBeDefined();
    expect(router.refresh).toBeDefined();
    expect(router.back).toBeDefined();
    expect(router.forward).toBeDefined();
  });
}); 