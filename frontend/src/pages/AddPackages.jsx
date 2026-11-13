function AddPackage() {
  async function addPackage(event) {
    event.preventDefault();
    const form = new FormData(event.target);

    const response = await fetch("http://127.0.0.1:8000/packages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        token: localStorage.getItem("access_token"),
      },
      body: JSON.stringify({
        package_name: form.get("package_name"),
        destination: form.get("destination"),
        weight: Number(form.get("weight")),
        arrival_date: form.get("arrival_date"),
      }),
    });

    if (response.ok) {
      alert("Package added");
    } else {
      alert("Could not add package");
    }
  }

  return (
    <form onSubmit={addPackage}>
      <h2>Add Package</h2>
      <input name="package_name" placeholder="Package name" required />
      <input name="destination" placeholder="Destination" required />
      <input name="weight" type="number" placeholder="Weight" required />
      <input name="arrival_date" type="date" required />
      <button>Add Package</button>
    </form>
  );
}

export default AddPackage;