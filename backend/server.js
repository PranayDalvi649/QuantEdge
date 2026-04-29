const express = require("express");
const app = express();

app.get("/", (req, res) => {
  res.send("Backend running 🚀");
});

app.listen(5000, () => console.log("Server on 5000"));