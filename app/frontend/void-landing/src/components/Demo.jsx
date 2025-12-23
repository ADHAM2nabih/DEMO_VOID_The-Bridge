import { useState, useRef, useCallback } from 'react';
import Webcam from 'react-webcam';
import { useLanguage } from '../context/LanguageContext';
import { Send, Bot, Video, Keyboard, Loader2, Mic, Circle, Square } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function Demo() {
  const { t, lang } = useLanguage();
  
  // State Management
  const [mode, setMode] = useState('text-to-sign'); // 'text-to-sign' OR 'sign-to-text'
  const [inputText, setInputText] = useState('');
  const [outputText, setOutputText] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  
  // Camera & Recording States
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  
  const webcamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);

  // ---------------------------------------------------------
  // 🔗 API INTEGRATION (Send Video Blob to Backend)
  // ---------------------------------------------------------
  const sendVideoToBackend = async (videoBlob) => {
    setIsProcessing(true);
    setOutputText(''); // Reset previous output

    const formData = new FormData();
    // "file" لازم يطابق اسم الباراميتر في FastAPI: file: UploadFile
    formData.append('file', videoBlob, 'sign_video.webm');

    try {
      // بنبعت لـ /api/predict عشان الـ Nginx بيحولها للباك إند
      const response = await fetch('/api/predict', {
        method: 'POST',
        body: formData, // FormData doesn't need Content-Type header manually
      });

      if (!response.ok) {
        throw new Error(`Server Error: ${response.status}`);
      }

      const data = await response.json();
      
      // النتيجة جاية في { "result": "..." }
      setOutputText(data.result || (lang === 'ar' ? "لم يتم التعرف" : "Unknown"));

    } catch (error) {
      console.error("API Error:", error);
      setOutputText(lang === 'ar' ? "خطأ في الاتصال بالسيرفر" : "Connection Error");
    } finally {
      setIsProcessing(false);
    }
  };

  // ---------------------------------------------------------
  // 🎥 Recording Logic
  // ---------------------------------------------------------
  
  // 1. Start Recording
  const startRecording = useCallback(() => {
    setIsRecording(true);
    chunksRef.current = []; // Reset chunks

    if (webcamRef.current && webcamRef.current.video.srcObject) {
      const stream = webcamRef.current.video.srcObject;
      
      // Create MediaRecorder
      mediaRecorderRef.current = new MediaRecorder(stream, {
        mimeType: "video/webm"
      });

      // Collect data chunks
      mediaRecorderRef.current.ondataavailable = (e) => {
        if (e.data && e.data.size > 0) {
          chunksRef.current.push(e.data);
        }
      };

      // On Stop -> Create Blob & Send
      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: "video/webm" });
        sendVideoToBackend(blob);
      };

      mediaRecorderRef.current.start();
    }
  }, [webcamRef]);

  // 2. Stop Recording
  const stopRecording = useCallback(() => {
    setIsRecording(false);
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
    }
  }, []);

  // 3. Toggle Camera Button Handler
  const handleCameraToggle = () => {
    if (!isCameraActive) {
      // Open Camera
      setIsCameraActive(true);
      setOutputText('');
    } else {
      // If camera is open...
      if (!isRecording) {
        // Start Recording
        startRecording();
      } else {
        // Stop Recording & Send
        stopRecording();
      }
    }
  };

  // ---------------------------------------------------------
  // ⌨️ Text Logic
  // ---------------------------------------------------------
  const handleTextSubmit = async () => {
    if (!inputText.trim()) return;
    setIsProcessing(true);
    // Simulation for Text-to-Sign (Avatar)
    setTimeout(() => {
        console.log("Avatar Text Sent:", inputText);
        setIsProcessing(false);
    }, 1500);
  };

  return (
    <section id="demo" className="py-24 bg-slate-50 relative overflow-hidden">
      
      {/* Header */}
      <div className="max-w-4xl mx-auto px-4 text-center mb-12 relative z-10">
        <motion.h2 
          initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}
          className="text-4xl md:text-5xl font-black text-slate-900 mb-6"
        >
          {t.demo.title}
        </motion.h2>
        <p className="text-xl text-slate-600 max-w-2xl mx-auto">{t.demo.subtitle}</p>
      </div>

      {/* Mode Switcher (Tabs) */}
      <div className="flex justify-center mb-10 relative z-10">
        <div className="bg-white p-1.5 rounded-full shadow-md border border-slate-200 inline-flex">
          <button 
            onClick={() => { setMode('text-to-sign'); setIsCameraActive(false); setIsRecording(false); }}
            className={`px-6 py-3 rounded-full flex items-center gap-2 font-bold transition-all duration-300 ${mode === 'text-to-sign' ? 'bg-teal-600 text-white shadow-lg' : 'text-slate-500 hover:bg-slate-50'}`}
          >
            <Keyboard size={20} /> {t.demo.mode_text_to_sign}
          </button>
          <button 
            onClick={() => { setMode('sign-to-text'); setInputText(''); }}
            className={`px-6 py-3 rounded-full flex items-center gap-2 font-bold transition-all duration-300 ${mode === 'sign-to-text' ? 'bg-teal-600 text-white shadow-lg' : 'text-slate-500 hover:bg-slate-50'}`}
          >
            <Video size={20} /> {t.demo.mode_sign_to_text}
          </button>
        </div>
      </div>

      {/* Main Interface Container */}
      <div className="max-w-6xl mx-auto px-4 relative z-10">
        <motion.div 
          layout
          className="bg-white rounded-3xl shadow-2xl shadow-slate-200/50 overflow-hidden border border-slate-100 flex flex-col lg:flex-row min-h-[600px]"
        >
          
          {/* =========================================================
              LEFT SIDE: INPUT (Changes based on Mode)
             ========================================================= */}
          <div className="lg:w-1/2 p-6 flex flex-col border-b lg:border-b-0 lg:border-r border-slate-100 bg-slate-50/30">
            
            <h3 className="font-bold text-slate-700 flex items-center gap-2 mb-4">
              <span className={`w-3 h-3 rounded-full ${mode === 'sign-to-text' && isRecording ? 'bg-red-500 animate-pulse' : 'bg-teal-500'}`}></span>
              {mode === 'text-to-sign' ? (lang === 'ar' ? 'أدخل النص' : 'Input Text') : (lang === 'ar' ? 'كاميرتك' : 'Your Camera')}
            </h3>

            <AnimatePresence mode="wait">
              {mode === 'text-to-sign' ? (
                // 1. Text Input Mode
                <motion.div 
                  key="text-input"
                  initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }}
                  className="flex-1 flex flex-col"
                >
                  <div className="flex-1 bg-white rounded-2xl p-4 shadow-inner border border-slate-200 focus-within:ring-2 focus-within:ring-teal-500/20 transition-all">
                    <textarea 
                      className="w-full h-full bg-transparent border-none focus:ring-0 resize-none text-slate-800 text-lg leading-relaxed placeholder:text-slate-400"
                      placeholder={t.demo.input_placeholder}
                      value={inputText}
                      onChange={(e) => setInputText(e.target.value)}
                      dir={lang === 'ar' ? 'rtl' : 'ltr'}
                    />
                  </div>
                  <button 
                    onClick={handleTextSubmit}
                    disabled={isProcessing || !inputText.trim()}
                    className="mt-4 w-full bg-teal-600 text-white py-4 rounded-xl font-bold hover:bg-teal-700 transition flex justify-center items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isProcessing ? <Loader2 className="animate-spin" /> : <Send size={20} className={lang === 'ar' ? 'rotate-180' : ''} />}
                    {isProcessing ? t.demo.output_text_processing : t.demo.translate_btn}
                  </button>
                </motion.div>

              ) : (
                // 2. Camera Input Mode
                <motion.div 
                  key="camera-input"
                  initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }}
                  className="flex-1 flex flex-col"
                >
                  <div className="flex-1 bg-black rounded-2xl overflow-hidden relative shadow-inner group">
                    {isCameraActive ? (
                      <>
                        <Webcam 
                          ref={webcamRef}
                          audio={false}
                          screenshotFormat="image/jpeg"
                          className="w-full h-full object-cover transform scale-x-[-1]" // Mirror effect
                          videoConstraints={{
                            width: 640,
                            height: 480,
                            facingMode: "user"
                          }}
                        />
                        {/* Recording Indicator */}
                        {isRecording && (
                            <div className="absolute top-4 left-4 bg-red-600 text-white flex items-center gap-2 px-3 py-1 rounded-full animate-pulse z-30 font-bold text-xs">
                                <div className="w-2 h-2 bg-white rounded-full"></div> REC
                            </div>
                        )}
                        
                        {/* Scanning Effect (Only visual) */}
                        <div className="absolute inset-0 bg-teal-500/5 z-10 pointer-events-none"></div>
                        <div className="absolute top-0 left-0 w-full h-1 bg-teal-400 shadow-[0_0_15px_rgba(45,212,191,0.8)] animate-[scan_2s_ease-in-out_infinite] z-20"></div>
                      </>
                    ) : (
                      <div className="w-full h-full flex flex-col items-center justify-center text-slate-500 bg-slate-100">
                        <Video size={64} className="mb-4 opacity-50" />
                        <p>{t.demo.camera_permission}</p>
                      </div>
                    )}
                  </div>

                  {/* Camera Control Button */}
                  <button 
                    onClick={handleCameraToggle}
                    disabled={isProcessing}
                    className={`mt-4 w-full py-4 rounded-xl font-bold transition flex justify-center items-center gap-2
                      ${!isCameraActive 
                        ? 'bg-teal-600 text-white hover:bg-teal-700 shadow-lg' 
                        : isRecording 
                            ? 'bg-red-500 text-white hover:bg-red-600 shadow-lg animate-pulse'
                            : 'bg-slate-800 text-white hover:bg-slate-900'
                      }`}
                  >
                    {/* Logic for Button Text/Icon */}
                    {!isCameraActive ? (
                        <> {t.demo.camera_btn_start} <Video size={20} /> </>
                    ) : isRecording ? (
                        <> {lang === 'ar' ? 'إنهاء التسجيل' : 'Stop Recording'} <Square size={20} fill="currentColor" /> </>
                    ) : (
                        <> {lang === 'ar' ? 'بدء التسجيل' : 'Start Recording'} <Circle size={20} fill="currentColor" className="text-red-500" /> </>
                    )}
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>


          {/* =========================================================
              RIGHT SIDE: OUTPUT (Changes based on Mode)
             ========================================================= */}
          <div className="lg:w-1/2 bg-slate-900 p-8 flex flex-col relative overflow-hidden">
             
             {/* Tech Background decoration */}
             <div className="absolute inset-0 opacity-10 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] pointer-events-none"></div>
             
             {/* Output Header */}
             <div className="flex justify-between items-center mb-6 relative z-10 text-teal-500/80 font-mono text-sm">
                <span className="flex items-center gap-2">
                   <Bot size={16} /> {mode === 'text-to-sign' ? 'AI AVATAR OUTPUT' : 'AI TEXT OUTPUT'}
                </span>
                <span className="bg-slate-800 px-2 py-1 rounded text-xs">v1.2.0-beta</span>
             </div>

             {/* Output Content */}
             <div className="flex-1 flex flex-col items-center justify-center relative z-10 w-full">
                <AnimatePresence mode="wait">
                  
                  {/* CASE 1: Processing State */}
                  {isProcessing && (
                    <motion.div 
                      key="processing"
                      initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                      className="text-center"
                    >
                       <div className="w-16 h-16 border-4 border-teal-500/30 border-t-teal-500 rounded-full animate-spin mx-auto mb-4"></div>
                       <p className="text-teal-400 animate-pulse">{t.demo.output_text_processing}</p>
                    </motion.div>
                  )}

                  {/* CASE 2: Text-to-Sign (Show Avatar) */}
                  {!isProcessing && mode === 'text-to-sign' && (
                    <motion.div 
                      key="avatar-output"
                      initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}
                      className="relative group cursor-pointer w-full flex flex-col items-center"
                    >
                      {/* Avatar Placeholder */}
                      <div className="w-64 h-64 bg-gradient-to-b from-teal-900 to-slate-800 rounded-full flex items-center justify-center border-4 border-slate-700 shadow-[0_0_50px_rgba(20,184,166,0.1)] group-hover:shadow-[0_0_80px_rgba(20,184,166,0.3)] transition-all duration-500 relative">
                         <div className="absolute inset-0 rounded-full bg-teal-500/10 blur-xl group-hover:blur-2xl transition-all"></div>
                         <Bot size={100} className="text-teal-500/50 group-hover:text-teal-400 transition-all duration-500 relative z-10" />
                      </div>
                      <div className="mt-8 text-center">
                        <p className="text-slate-400 text-lg mb-2">{t.demo.avatar_placeholder_title}</p>
                        <p className="text-slate-600 text-sm">{t.demo.avatar_placeholder_subtitle}</p>
                      </div>
                    </motion.div>
                  )}

                  {/* CASE 3: Sign-to-Text (Show Recognized Text) */}
                  {!isProcessing && mode === 'sign-to-text' && (
                    <motion.div 
                      key="text-output"
                      initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                      className="w-full bg-slate-800/50 backdrop-blur-md rounded-2xl p-6 border border-slate-700 min-h-[200px] flex flex-col"
                    >
                       <h4 className="text-slate-400 text-sm font-bold mb-4 border-b border-slate-700 pb-2">
                         {lang === 'ar' ? 'الترجمة الفورية' : 'Live Translation'}
                       </h4>
                       <p className={`text-2xl font-medium leading-relaxed ${outputText ? 'text-white' : 'text-slate-600'}`}>
                         {outputText || t.demo.output_text_result}
                       </p>
                       {outputText && (
                          <div className="mt-auto pt-4 flex justify-end">
                             <button className="text-teal-400 hover:text-teal-300 text-sm flex items-center gap-1">
                                <Mic size={14} /> {lang === 'ar' ? 'استماع' : 'Listen'}
                             </button>
                          </div>
                       )}
                    </motion.div>
                  )}

                </AnimatePresence>
             </div>

          </div>
        </motion.div>
      </div>

      {/* CSS Animation for Scanner Line */}
      <style>{`
        @keyframes scan {
          0% { top: 0; opacity: 0; }
          10% { opacity: 1; }
          90% { opacity: 1; }
          100% { top: 100%; opacity: 0; }
        }
      `}</style>
    </section>
  );
}