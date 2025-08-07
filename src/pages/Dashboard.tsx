import Layout from "../layouts/Layout";
import { InputPanel } from "../components/InputPanel";
import { EmptyState } from "../components/EmptyState";

const Dashboard = () => {
    const handleAnalyze = (text: string) => {
        console.log("Analyzing:", text);
    };

    return (
        <Layout>
            <InputPanel onAnalyze={handleAnalyze} isLoading={false} />
            <EmptyState />
        </Layout>
    );
};

export default Dashboard;
