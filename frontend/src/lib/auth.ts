export const authStorage = {
  getToken: () => (typeof window !== "undefined" ? localStorage.getItem("access_token") : null),
  setToken: (token: string) => localStorage.setItem("access_token", token),
  getRole: () => (typeof window !== "undefined" ? localStorage.getItem("role") : null),
  setRole: (role: string) => localStorage.setItem("role", role),
  clearToken: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("role");
  },
  isLoggedIn: () => !!authStorage.getToken(),
  isAdmin: () => authStorage.getRole() === "admin",
};