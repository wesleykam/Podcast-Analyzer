import { useState } from "react";
import Layout from "../layouts/Layout";
import { InputPanel } from "../components/InputPanel";
import { EmptyState } from "../components/EmptyState";
import { ResultsDashboard } from "../components/ResultsDashboard";

interface ActionableInsight {
    header: string;
    detail: string;
}

const Dashboard = () => {
    const [summary, setSummary] = useState<string[]>([]);
    const [organizations, setOrganizations] = useState<string[]>([]);
    const [insights, setInsights] = useState<ActionableInsight[]>([]);

    const handleAnalyze = (data: string) => {
        try {
            const parsedData = JSON.parse(data);

            setSummary(parsedData.summary);
            setOrganizations(parsedData.mentioned_organizations);
            setInsights(parsedData.actionable_insights);
        } catch (error) {
            console.error("Failed to parse data:", error);
        }
    };

    return (
        <Layout>
            <InputPanel onAnalyze={handleAnalyze} isLoading={false} />

            {summary.length > 0 && organizations.length > 0 && insights.length > 0 ? (
                <ResultsDashboard
                    summary={summary}
                    organizations={organizations}
                    insights={insights}
                />
            ) : <EmptyState />}
        </Layout>
    );
};

export default Dashboard;
