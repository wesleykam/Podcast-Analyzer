import React, { useState, useRef } from "react";
import { Upload, Sparkles, Link, Type } from "lucide-react";
import axios from 'axios';
import "./InputPanel.css";
import Loading from './Loading';

interface InputPanelProps {
    onAnalyze: (data: any) => void;
    isLoading: boolean;
}

type InputMode = 'url' | 'text';

export function InputPanel({ onAnalyze }: InputPanelProps) {
    const [inputText, setInputText] = useState("");
    const [inputMode, setInputMode] = useState<InputMode>('url');
    const [isDragging, setIsDragging] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const handleSubmit = async () => {
        if (inputText.trim()) {
            try {
                setIsLoading(true);

                const endpoint = inputMode === 'url' ? 'http://localhost:5000/analyze-url' : 'http://localhost:5000/analyze-text';
                const payload = inputMode === 'url' ? { url: inputText.trim() } : { text: inputText.trim() };

                const response = await axios.post(endpoint, payload);

                // Pass the full response data to the parent component
                onAnalyze(response.data);
            } catch (error) {
                console.error('Error analyzing input:', error);
            } finally {
                setIsLoading(false);
            }
        }
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
            e.preventDefault();
            handleSubmit();
        }
    };

    const handleModeChange = (mode: InputMode) => {
        setInputMode(mode);
        setInputText(""); // Clear input when switching modes
    };

    const handleFileSelect = (file: File) => {
        const reader = new FileReader();
        reader.onload = (e) => {
            const text = e.target?.result as string;
            setInputText(text);
            setInputMode('text'); // Switch to text mode when file is uploaded
        };
        reader.readAsText(file);
    };

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);

        const files = Array.from(e.dataTransfer.files);
        const textFile = files.find(file => file.type === "text/plain" || file.name.endsWith('.txt'));

        if (textFile) {
            handleFileSelect(textFile);
        }
    };

    const isValidUrl = (string: string) => {
        try {
            new URL(string);
            return true;
        } catch (_) {
            return false;
        }
    };

    const isSubmitDisabled = () => {
        if (!inputText.trim() || isLoading) return true;
        if (inputMode === 'url' && !isValidUrl(inputText.trim())) return true;
        return false;
    };

    return (
        <div className="input-panel-container">
            <div className="card">
                <div className="input-panel-content">
                    {/* Input Mode Toggle */}
                    <div className="input-mode-toggle">
                        <label className="input-panel-label">
                            Transcript Input
                        </label>

                        <div className="input-mode-buttons" role="tablist" aria-label="Input mode selection">
                            <button
                                onClick={() => handleModeChange('url')}
                                disabled={isLoading}
                                className={`input-mode-button ${inputMode === 'url' ? 'active' : ''}`}
                                role="tab"
                                aria-selected={inputMode === 'url'}
                                aria-controls="input-panel"
                            >
                                <Link className="icon" size={16} />
                                <span>URL</span>
                            </button>

                            <button
                                onClick={() => handleModeChange('text')}
                                disabled={isLoading}
                                className={`input-mode-button ${inputMode === 'text' ? 'active' : ''}`}
                                role="tab"
                                aria-selected={inputMode === 'text'}
                                aria-controls="input-panel"
                            >
                                <Type className="icon" size={16} />
                                <span>Text</span>
                            </button>
                        </div>
                    </div>

                    {/* Main Input Area */}
                    <div className="main-input-area" id="input-panel" role="tabpanel">
                        <div
                            className={`input-area ${isDragging ? 'dragging' : ''}`}
                            onDragOver={inputMode === 'text' ? handleDragOver : undefined}
                            onDragLeave={inputMode === 'text' ? handleDragLeave : undefined}
                            onDrop={inputMode === 'text' ? handleDrop : undefined}
                        >
                            {inputMode === 'url' ? (
                                <input
                                    id="transcript-input"
                                    type="url"
                                    placeholder="https://example.com/transcript-url"
                                    value={inputText}
                                    onChange={(e) => setInputText(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    className="url-input"
                                    disabled={isLoading}
                                    aria-describedby="input-help"
                                    aria-invalid={inputText.trim() && !isValidUrl(inputText.trim()) ? 'true' : 'false'}
                                />
                            ) : (
                                <textarea
                                    id="transcript-input"
                                    placeholder="Paste your transcript text here..."
                                    value={inputText}
                                    onChange={(e) => setInputText(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    className="text-input"
                                    disabled={isLoading}
                                    aria-describedby="input-help"
                                />
                            )}

                            {isDragging && inputMode === 'text' && (
                                <div className="drag-overlay">
                                    <div className="drag-text">
                                        Drop your .txt file here
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Dynamic Help Text */}
                        <div id="input-help" className="help-text">
                            <p>
                                {inputMode === 'url' ? (
                                    <>Compatible with <span className="highlight">ThisWeekHealth.com</span> & <span className="highlight">YouTube</span> transcript URLs</>
                                ) : (
                                    <>Compatible with <span className="highlight">ThisWeekHealth.com</span> & <span className="highlight">YouTube</span> transcript text</>
                                )}
                            </p>

                            {/* URL Validation Error */}
                            {inputMode === 'url' && inputText.trim() && !isValidUrl(inputText.trim()) && (
                                <p className="error-text" role="alert">
                                    Please enter a valid URL
                                </p>
                            )}
                        </div>
                    </div>

                    {/* File Upload Option - Only show in text mode */}
                    {inputMode === 'text' && (
                        <div className="file-upload">
                            <div className="upload-controls">
                                <button
                                    onClick={() => fileInputRef.current?.click()}
                                    disabled={isLoading}
                                    className="upload-button"
                                    aria-label="Upload transcript file"
                                >
                                    <Upload className="icon" size={16} />
                                    Upload .txt file
                                </button>

                                <span className="upload-hint">
                                    or drag and drop a file above
                                </span>
                            </div>
                        </div>
                    )}

                    {/* Analyze Button */}
                    <div className="analyze-controls">
                        <button
                            onClick={handleSubmit}
                            disabled={isSubmitDisabled()}
                            className="analyze-button"
                            aria-label={`Analyze ${inputMode === 'url' ? 'transcript from URL' : 'transcript text'}`}
                        >
                            <Sparkles className="icon" />
                            <span>
                                Analyze {inputMode === 'url' ? 'URL' : 'Text'}
                            </span>
                        </button>

                        <p className="powered-by">
                            Powered by <span className="highlight">OpenAI</span> / <span className="highlight">Claude</span>
                        </p>
                    </div>

                    {/* Loading Component */}
                    {isLoading && <Loading />}

                    {/* Keyboard Shortcut Hint */}
                    <p className="shortcut-hint">
                        Press <kbd>Ctrl</kbd> + <kbd>Enter</kbd> to analyze
                    </p>
                </div>
            </div>
        </div>
    );
}
