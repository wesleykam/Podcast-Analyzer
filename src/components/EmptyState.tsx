import "./EmptyState.css";
import { FileText, Upload, Building2, TargetIcon } from "lucide-react";

export function EmptyState() {
    return (
        <div className="empty-state-container">
            <div className="empty-state-card card">
                <div className="empty-state-illustration">
                    <div className="empty-state-icon">
                        <FileText className="icon-file-text" />
                    </div>
                    <div className="empty-state-upload-icon">
                        <Upload className="icon-upload" />
                    </div>
                </div>

                <div className="empty-state-message">
                    <h3 className="empty-state-title">Awaiting your transcript...</h3>
                    <p className="empty-state-description">
                        Upload a transcript or paste text above to get started with AI-powered analysis of podcast content.
                    </p>
                </div>

                <div className="empty-state-features">
                    <div className="feature-item">
                        <div className="feature-icon feature-icon-blue">
                            <FileText className="icon-feature"/>
                        </div>
                        <h4 className="feature-title">Key Takeaways</h4>
                        <p className="feature-description">Extract main points and insights</p>
                    </div>

                    <div className="feature-item">
                        <div className="feature-icon feature-icon-green">
                            <Building2 className="icon-feature" />
                        </div>
                        <h4 className="feature-title">Organizations</h4>
                        <p className="feature-description">Identify mentioned companies</p>
                    </div>

                    <div className="feature-item">
                        <div className="feature-icon feature-icon-purple">
                            <TargetIcon className="icon-feature" />
                        </div>
                        <h4 className="feature-title">Action Items</h4>
                        <p className="feature-description">Generate actionable insights</p>
                    </div>
                </div>
            </div>
        </div>
    );
}