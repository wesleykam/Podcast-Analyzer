import Layout from "../layouts/Layout";
import { InputPanel } from "../components/InputPanel";
import { EmptyState } from "../components/EmptyState";
import { ResultsDashboard } from "../components/ResultsDashboard";

const Dashboard = () => {
    const handleAnalyze = (text: string) => {
        console.log("Analyzing:", text);
    };

    return (
        <Layout>
            <InputPanel onAnalyze={handleAnalyze} isLoading={false} />
            <EmptyState />
            <ResultsDashboard
                summary={["Summary Item 1", "Summary Item 2"]}
                organizations={[{ id: "1", name: "Org 1", type: "company" }]}
                insights={[{ id: "1", title: "Insight 1", rationale: "Rationale 1", tag: "strategy" }]}
            />
        </Layout>
    );
};

export default Dashboard;
