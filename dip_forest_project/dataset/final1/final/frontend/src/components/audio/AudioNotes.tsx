import React, { useRef, useState } from "react";

interface AudioNote {
  id: string;
  blob: Blob;
  url: string;
  createdAt: Date;
}

const AudioNotes: React.FC = () => {
  const [notes, setNotes] = useState<AudioNote[]>([]);
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const handleStartRecording = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

    const mediaRecorder = new MediaRecorder(stream);
    mediaRecorderRef.current = mediaRecorder;

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) {
        chunksRef.current.push(e.data);
      }
    };

    mediaRecorder.onstop = () => {
      const blob = new Blob(chunksRef.current, { type: "audio/webm" });
      const url = URL.createObjectURL(blob);

      const newNote: AudioNote = {
        id: Date.now().toString(),
        blob,
        url,
        createdAt: new Date(),
      };

      setNotes((prev) => [newNote, ...prev]);
      chunksRef.current = [];
    };

    mediaRecorder.start();
    setRecording(true);
  };

  const handleStopRecording = () => {
    mediaRecorderRef.current?.stop();
    setRecording(false);
  };

  const handleDeleteNote = (id: string) => {
    setNotes((prev) => prev.filter((note) => note.id !== id));
  };

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Audio Notes</h2>

      <div className="flex gap-4 mb-6">
        {!recording ? (
          <button
            onClick={handleStartRecording}
            className="px-4 py-2 bg-green-600 text-white rounded"
          >
            🎤 Start Recording
          </button>
        ) : (
          <button
            onClick={handleStopRecording}
            className="px-4 py-2 bg-red-600 text-white rounded"
          >
            ⏹️ Stop Recording
          </button>
        )}
      </div>

      {notes.length === 0 ? (
        <p className="text-gray-500">No audio notes yet.</p>
      ) : (
        <div className="space-y-4">
          {notes.map((note) => (
            <div
              key={note.id}
              className="flex items-center justify-between bg-gray-100 p-3 rounded"
            >
              <audio controls src={note.url} />
              <button
                onClick={() => handleDeleteNote(note.id)}
                className="ml-4 text-red-600 hover:text-red-800"
              >
                ❌ Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default AudioNotes;
