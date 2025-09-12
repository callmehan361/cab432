const express = require("express");
const multer = require("multer");
const ffmpeg = require("fluent-ffmpeg");
const ffmpegPath = require("ffmpeg-static");
const { v4: uuidv4 } = require("uuid");
const fs = require("fs");
const path = require("path");
const authMiddleware = require("../middleware/authMiddleware");

ffmpeg.setFfmpegPath(ffmpegPath);
const router = express.Router();
const jobsFile = path.join(__dirname, "../models/jobs.json");

// File upload storage
const storage = multer.diskStorage({
  destination: "uploads/",
  filename: (req, file, cb) => cb(null, Date.now() + "-" + file.originalname),
});
const upload = multer({ storage });

// Upload + Transcode
router.post("/upload", authMiddleware, upload.single("video"), (req, res) => {
  if (!req.file) return res.status(400).json({ message: "No file uploaded" });

  const jobId = uuidv4();
  const outputFile = `outputs/${jobId}.mp4`;

  // Store job metadata
  const jobs = JSON.parse(fs.readFileSync(jobsFile, "utf-8"));
  jobs.push({ id: jobId, user: req.user.username, status: "processing" });
  fs.writeFileSync(jobsFile, JSON.stringify(jobs, null, 2));

  // CPU-intensive transcoding
  ffmpeg(req.file.path)
    .outputOptions(["-preset veryslow", "-crf 28"]) // heavy CPU usage
    .output(outputFile)
    .on("end", () => {
      const jobs = JSON.parse(fs.readFileSync(jobsFile, "utf-8"));
      const job = jobs.find(j => j.id === jobId);
      job.status = "completed";
      job.output = outputFile;
      fs.writeFileSync(jobsFile, JSON.stringify(jobs, null, 2));
    })
    .on("error", (err) => {
      const jobs = JSON.parse(fs.readFileSync(jobsFile, "utf-8"));
      const job = jobs.find(j => j.id === jobId);
      job.status = "failed";
      fs.writeFileSync(jobsFile, JSON.stringify(jobs, null, 2));
    })
    .run();

  res.json({ message: "Transcoding started", jobId });
});

// Job status
router.get("/status/:id", authMiddleware, (req, res) => {
  const jobs = JSON.parse(fs.readFileSync(jobsFile, "utf-8"));
  const job = jobs.find(j => j.id === req.params.id);
  if (!job) return res.status(404).json({ message: "Job not found" });
  res.json(job);
});

module.exports = router;
