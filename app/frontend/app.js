let rec;
let chunks = [];

navigator.mediaDevices.getUserMedia({ video: true }).then(stream => {
  const video = document.getElementById("video");
  video.srcObject = stream;

  rec = new MediaRecorder(stream);

  rec.ondataavailable = e => {
    chunks.push(e.data);
  };

  rec.onstop = async () => {
    const blob = new Blob(chunks, { type: "video/mp4" });
    chunks = [];

    const fd = new FormData();
    fd.append("file", blob, "record.mp4");

    const res = await fetch("http://localhost:8000/predict", {
      method: "POST",
      body: fd
    });

    const json = await res.json();
    document.getElementById("res").innerText = json.result;
  };
});

function start() {
  chunks = [];
  rec.start();
  document.getElementById("res").innerText = "Recording...";
}

function stop() {
  rec.stop();
}
