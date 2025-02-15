document.getElementById('process-btn').addEventListener('click', async () => {
    const pdfFile = document.getElementById('pdf-file').files[0];

    if (!pdfFile) {
        alert('Please upload a PDF file!');
        return;
    }

    const formData = new FormData();
    formData.append('pdf', pdfFile);

    try {
        const response = await fetch('http://localhost:8000/process_pdf', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const audioBlob = await response.blob();
            const audioURL = URL.createObjectURL(audioBlob);
            const audioPlayer = document.getElementById('audio-player');
            audioPlayer.src = audioURL;
            audioPlayer.play();
        } else {
            alert('Error processing PDF: ' + response.statusText);
        }
    } catch (error) {
        console.error('Error during processing:', error);
    }
});
