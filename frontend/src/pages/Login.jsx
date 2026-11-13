function Login() {
  async function login(event) {
    event.preventDefault();

    const form = new FormData(event.target);

    const response = await fetch("http://127.0.0.1:8000/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        username: form.get("username"),
        password: form.get("password"),
      }),
    });

    const result = await response.json();

    if (response.ok) {
      localStorage.setItem("access_token", result.access_token);
      localStorage.setItem("refresh_token", result.refresh_token);
      alert("Login successful");
    } else {
      alert("Login failed");
    }
  }

  return (
    <form onSubmit={login}>
      <h2>Login</h2>
      <input name="username" placeholder="Username" required />
      <input name="password" type="password" placeholder="Password" required />
      <button type="submit">Login</button>
    </form>
  );
}

export default Login;