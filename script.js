document.getElementById("processBtn").addEventListener("click", async () => {
    const speechFile = document.getElementById("speechFile").files[0];
    const noiseFile = document.getElementById("noiseFile").files[0];
    const statusDiv = document.getElementById("status");
  
    if (!speechFile || !noiseFile) {
      alert("Please upload both clean speech and rain noise files!");
      return;
    }
  
    statusDiv.innerText = "⏳ Processing... please wait.";
  
    // Display the original audio
    document.getElementById("originalAudio").src = URL.createObjectURL(speechFile);
  
    // Prepare form data
    const formData = new FormData();
    formData.append("speech", speechFile);
    formData.append("noise", noiseFile);
  
    try {
      const response = await fetch("/process", {
        method: "POST",
        body: formData
      });
  
      if (!response.ok) {
        const text = await response.text();
        throw new Error("Backend error: " + text);
      }
  
      const blob = await response.blob();
      const audioUrl = URL.createObjectURL(blob);
  
      document.getElementById("filteredAudio").src = audioUrl;
      statusDiv.innerText = "✅ Processing complete! Listen to the filtered speech below.";
    } catch (error) {
      statusDiv.innerText = "❌ Error: " + error.message;
    }
  });
  