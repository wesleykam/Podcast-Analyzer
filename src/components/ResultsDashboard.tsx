import { Copy, Download, MessageSquare, Search, Users, Building2 } from "lucide-react";
import "./ResultsDashboard.css";
import { useState } from "react";

interface ResultsDashboardProps {
    summary: string[];
    organizations: string[];
    insights: string[];
}

export function ResultsDashboard({
    summary,
    organizations,
    insights,
}: ResultsDashboardProps) {
    const [searchTerm, setSearchTerm] = useState("");
    const filteredOrganizations = organizations.filter((org) =>
        org.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const handleExport = (type: "copy" | "pdf" | "slack") => {
        switch (type) {
            case "copy":
                const exportText = `
Summary:
${summary}

Organizations Mentioned:
${organizations.map((org) => `• ${org}`).join("\n")}

Key Insights:
${insights.map((insight) => `• ${insight}`).join("\n")}
                `;
                navigator.clipboard.writeText(exportText.trim());
                break;
            case "pdf":
                console.log("Downloading PDF...");
                break;
            case "slack":
                console.log("Posting to Slack...");
                break;
        }
    };

    return (
        <div className="results-dashboard">
            <div className="card">
                <div className="card-header">
                    <h3 className="card-title">Key Takeaways</h3>
                </div>
                <div className="card-content">
                    <ol className="summary-list">
                        {summary.map((item, index) => (
                            <li key={index} className="summary-item">
                                <span className="summary-index">{index + 1}</span>
                                <span className="summary-text">{item}</span>
                            </li>
                        ))}
                    </ol>
                </div>
            </div>

            <div className="grid">
                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">
                            <Building2 className="icon" /> Mentioned Organizations & Tech
                        </h3>
                        <div className="search-container">
                            <Search className="search-icon" />
                            <input
                                type="text"
                                placeholder="Search organizations..."
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                className="search-input"
                            />
                        </div>
                    </div>
                    <div className="card-content">
                        <div className="badge-container">
                            {filteredOrganizations.map((org, index) => (
                                <span key={index} className="badge">
                                    {org}
                                </span>
                            ))}
                        </div>
                        {filteredOrganizations.length === 0 && (
                            <p className="no-results">No organizations found matching your search.</p>
                        )}
                    </div>
                </div>

                <div className="card">
                    <div className="card-header">
                        <h3 className="card-title">
                            <Users className="icon" /> Actionable Insights
                        </h3>
                    </div>
                    <div className="card-content">
                        <div className="insights-list">
                            {insights.map((insight, index) => (
                                <div key={index} className="insight-item">
                                    <div className="insight-icon">
                                        <span className="insight-index">{index + 1}</span>
                                    </div>
                                    <div className="insight-details">
                                        <p className="insight-text">{insight}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>

            <div className="card export-card">
                <div className="card-content">
                    <h3 className="export-title">Export & Share</h3>
                    <div className="export-buttons">
                        <button
                            onClick={() => handleExport("copy")}
                            className="export-button"
                        >
                            <Copy className="icon" /> Copy
                        </button>
                        <button
                            onClick={() => handleExport("pdf")}
                            className="export-button"
                        >
                            <Download className="icon" /> PDF
                        </button>
                        <button
                            onClick={() => handleExport("slack")}
                            className="export-button"
                        >
                            <MessageSquare className="icon" /> Slack
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}