import React from 'react';
import './Loading.css';

const Loading: React.FC = () => {
    return (
        <div className="loading-container">
            <div className="spinner"></div>
            <p>Analyzing, please wait...</p>
        </div>
    );
};

export default Loading;
