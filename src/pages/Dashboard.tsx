import { useState } from "react";
import Layout from "../layouts/Layout";
import { InputPanel } from "../components/InputPanel";
import { EmptyState } from "../components/EmptyState";
import { ResultsDashboard } from "../components/ResultsDashboard";

interface ActionableInsight {
    header: string;
    detail: string;
}

interface DashboardData {
    summary: string[];
    mentioned_organizations: string[];
    actionable_insights: ActionableInsight[];
}

const Dashboard = () => {
    const [summary, setSummary] = useState<string[]>([]);
    const [organizations, setOrganizations] = useState<string[]>([]);
    const [insights, setInsights] = useState<ActionableInsight[]>([]);

    const handleAnalyze = (data: DashboardData) => {
        try {
            setSummary(data.summary);
            setOrganizations(data.mentioned_organizations);
            setInsights(data.actionable_insights);
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
