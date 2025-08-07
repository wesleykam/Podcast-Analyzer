import Layout from "../layouts/Layout";
import { InputPanel } from "../components/InputPanel";

const Dashboard = () => {
    const handleAnalyze = (text: string) => {
        console.log("Analyzing:", text);
    };

    return (
        <Layout>
            <InputPanel onAnalyze={handleAnalyze} isLoading={false} />
        </Layout>
    );
};

export default Dashboard;
