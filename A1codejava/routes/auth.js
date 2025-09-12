const express = require("express");
const fs = require("fs");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
const path = require("path");

const router = express.Router();
const usersFile = path.join(__dirname, "../models/userData.json");

// Register user
router.post("/register", (req, res) => {
  const { username, password } = req.body;
  const users = JSON.parse(fs.readFileSync(usersFile, "utf-8"));
  if (users.find(u => u.username === username)) {
    return res.status(400).json({ message: "User already exists" });
  }
  const hashed = bcrypt.hashSync(password, 10);
  users.push({ username, password: hashed });
  fs.writeFileSync(usersFile, JSON.stringify(users, null, 2));
  res.json({ message: "User registered successfully" });
});

// Login
router.post("/login", (req, res) => {
  const { username, password } = req.body;
  const users = JSON.parse(fs.readFileSync(usersFile, "utf-8"));
  const user = users.find(u => u.username === username);
  if (!user || !bcrypt.compareSync(password, user.password)) {
    return res.status(400).json({ message: "Invalid credentials" });
  }
  const token = jwt.sign({ username }, "secretkey", { expiresIn: "1h" });
  res.json({ token });
});

module.exports = router;
