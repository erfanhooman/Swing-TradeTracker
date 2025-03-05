import { motion } from "framer-motion";
import { Wallet } from "lucide-react";

const TotalBalanceCard = ({ Total_balance, loading, formatter }) => {
    return (
        <motion.div
            key="balance"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="w-64 h-30 p-5 bg-gradient-to-br from-violet-900 to-violet-800 rounded-lg shadow-xl flex flex-col justify-center"
        >
            <div className="flex items-center gap-3 text-violet-200 mb-2">
                <Wallet className="h-5 w-5" />
                <span className="text-l font-medium">Total Balance</span>
            </div>
            <div className="text-2xl font-bold text-white">
                {loading ? (
                    <motion.div
                        className="h-6 w-24 bg-gray-600 rounded animate-pulse"
                        initial={{ opacity: 0.3 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0.3 }}
                        transition={{ repeat: Infinity, duration: 0.8, ease: "easeInOut" }}
                    />
                ) : (
                    `$${formatter.format(Total_balance)}`
                )}
            </div>
        </motion.div>
    );
};

export default TotalBalanceCard;
