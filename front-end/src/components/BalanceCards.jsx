// src/components/BalanceCards.jsx
import { motion } from "framer-motion";
import { DollarSign, Coins } from "lucide-react";

const BalanceCards = ({ USDT_balance, Coin_balance, loading, formatter }) => {
    return (
        <div className="flex flex-col justify-between h-30">
            <div className="w-64 p-3 bg-gray-800 rounded-lg shadow-lg">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <DollarSign className="h-4 w-4 text-green-400" />
                        <span className="text-sm text-gray-400">On USDT</span>
                    </div>
                    <span className="text-xl font-bold text-white">
            {loading ? (
                <motion.div
                    className="h-5 w-16 bg-gray-600 rounded animate-pulse"
                    initial={{ opacity: 0.3 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0.3 }}
                    transition={{ repeat: Infinity, duration: 0.8, ease: "easeInOut" }}
                />
            ) : (
                `$${formatter.format(USDT_balance)}`
            )}
          </span>
                </div>
            </div>

            <div className="w-64 p-3 bg-gray-800 rounded-lg shadow-lg">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                        <Coins className="h-4 w-4 text-yellow-400" />
                        <span className="text-sm text-gray-400">On Coin</span>
                    </div>
                    <span className="text-xl font-bold text-white">
            {loading ? (
                <motion.div
                    className="h-5 w-16 bg-gray-600 rounded animate-pulse"
                    initial={{ opacity: 0.3 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0.3 }}
                    transition={{ repeat: Infinity, duration: 0.8, ease: "easeInOut" }}
                />
            ) : (
                `$${formatter.format(Coin_balance)}`
            )}
          </span>
                </div>
            </div>
        </div>
    );
};

export default BalanceCards;
