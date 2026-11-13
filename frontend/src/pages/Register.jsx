function Register() {
  async function register(event) {
    event.preventDefault();

    const form = new FormData(event.target);

    const response = await fetch("http://127.0.0.1:8000/register_user", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_name: form.get("user_name"),
        password: form.get("password"),
        role: form.get("role"),
      }),
    });
    
  const result = await response.json();
    if (response.ok) {
      alert("Registration successful");
    } else {
      alert(result.detail);
    }
  }

  return (
    <form onSubmit={register}>
      <h2>Register</h2>
      <input name="user_name" placeholder="Username" required />
      <input name="password" type="password" placeholder="Password" required />

      <select name="role">
        <option value="warehouse_staff">Warehouse staff</option>
        <option value="dispatcher">Dispatcher</option>
        <option value="admin">admin</option>
      </select>

      <button type="submit">Register</button>
    </form>
  );
}

export default Register;