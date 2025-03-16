import { useState, useEffect, Fragment } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Plus, Minus, ChevronDown, X, TrashIcon } from "lucide-react";
import {
    RefreshAccessToken,
    BalanceApi,
    DepositApi,
    WithdrawApi,
    OpenBoxesList,
    CloseBoxesList,
    TransactionsApi,
    LogoutApi,
    CloseBoxApi,
    TransactionApi,
    DeleteTransactionApi,
    SummaryApi
} from "../api.js";
import TransactionModal from "../components/TransactionModal";
import TotalBalanceCard from "../components/TotalBalanceCard";
import BalanceCards from "../components/BalanceCards";
import ErrorModal from "../components/ErrorModal";
import AddTransactionModal from '../components/AddTransactionModal';


function Dashboard() {
    const [totalBalance, setTotalBalance] = useState(null);
    const [usdtBalance, setUsdtBalance] = useState(null);
    const [coinBalance, setCoinBalance] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [transactionType, setTransactionType] = useState(null);
    const [amount, setAmount] = useState("");
    const [activeTab, setActiveTab] = useState("open");
    const [openBoxes, setOpenBoxes] = useState([]);
    const [closedBoxes, setClosedBoxes] = useState([]);
    const [boxesLoading, setBoxesLoading] = useState(true);
    const [expandedBoxId, setExpandedBoxId] = useState(null);
    const [transactions, setTransactions] = useState({});
    const [transactionLoading, setTransactionLoading] = useState(false);
    const [showAddTransaction, setShowAddTransaction] = useState(false);
    const [summary, setSummary] = useState(null);

    const fetchSummary = async () => {
        try {
            await RefreshAccessToken();
            const response = await SummaryApi();
            if (response.data.success) {
                setSummary(response.data.data);
            }
        } catch (err) {
            console.error("Error fetching summary:", err);
            setError("Failed to load summary data.");
        }
    };

    const handleAddTransaction = async (transactionData) => {
        setLoading(true);
        try {
            await RefreshAccessToken();
            const response = await TransactionApi(transactionData);

            if (!response.data.success) {
                return response;
            }

            setShowAddTransaction(false);
            location.reload();

        } catch (err) {
            return {
                data: {
                    success: false,
                    message: err.message || 'An unexpected error occurred',
                    data: {}
                }
            };
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteTransaction = async (transactionId) => {
        try {
            await RefreshAccessToken();
            const response = await DeleteTransactionApi(transactionId);
            if (response.status === 204) {
                location.reload();
            } else {
                setError("Failed to delete transaction.");
            }
        } catch (err) {
            setError("Error deleting transaction.");
        }
    };

    const formatNumber = (num) =>
        parseFloat(num)
            .toString()
            .replace(/(\.\d*?[1-9])0+$/, "$1")
            .replace(/\.0+$/, "");

    const formatter = new Intl.NumberFormat("en-US", {
        style: "decimal",
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    });

    const fetchBalance = async () => {
        setLoading(true);
        setError("");
        try {
            await RefreshAccessToken();
            const response = await BalanceApi();
            setTotalBalance(response.data.data.total_balance);
            setUsdtBalance(response.data.data.usdt_balance);
            setCoinBalance(response.data.data.coin_balance);
        } catch (err) {
            console.error("Error fetching balance:", err);
            setError("Failed to load balance.");
        } finally {
            setLoading(false);
        }
    };

    const fetchOpenBoxes = async () => {
        try {
            await RefreshAccessToken();
            const response = await OpenBoxesList();
            if (response.data.success) {
                setOpenBoxes(response.data.data);
            } else {
                setError("Failed to fetch open boxes.");
            }
        } catch (err) {
            setError("An error occurred while fetching open boxes.");
        }
    };

    const fetchClosedBoxes = async () => {
        try {
            await RefreshAccessToken();
            const response = await CloseBoxesList();
            if (response.data.success) {
                setClosedBoxes(response.data.data);
            } else {
                setError("Failed to fetch closed boxes.");
            }
        } catch (err) {
            setError("An error occurred while fetching closed boxes.");
        }
    };

    const fetchTransactions = async (boxId) => {
        setTransactionLoading(true);
        try {
            await RefreshAccessToken();
            console.log(boxId);
            const response = await TransactionsApi(boxId);
            if (response.data.success) {
                setTransactions((prev) => ({ ...prev, [boxId]: response.data.data }));
            }
        } catch {
            setError("Failed to fetch transactions.");
        } finally {
            setTransactionLoading(false);
        }
    };

    // Event handlers
    const handleLogout = async () => {
        setLoading(true);
        try {
            const refreshToken = localStorage.getItem("refreshToken");
            if (refreshToken) {
                await LogoutApi({ refresh: refreshToken });
                localStorage.removeItem("refreshToken");
                localStorage.removeItem("accessToken");
                window.location.href = "/login";
            } else {
                setError("No refresh token found.");
            }
        } catch (err) {
            console.error("Error during logout:", err);
            setError("Failed to log out.");
        } finally {
            setLoading(false);
        }
    };

    const handleCloseBox = async (boxId, e) => {
        e.stopPropagation();
        setLoading(true);
        setError("");
        try {
            await RefreshAccessToken();
            const response = await CloseBoxApi(boxId);
            if (response.data.success) {
                await fetchOpenBoxes();
                await fetchClosedBoxes();
            } else {
                setError(response.data.message || "Failed to close box");
            }
        } catch (err) {
            setError(err.response?.data?.message || "Failed to close box");
        } finally {
            setLoading(false);
        }
    };

    const handleExpand = async (boxId) => {
        if (expandedBoxId === boxId) {
            setExpandedBoxId(null);
            return;
        }
        setExpandedBoxId(null);
        setExpandedBoxId(boxId);
        if (!transactions[boxId]) {
            await fetchTransactions(boxId);
        }
    };

    const handleTransaction = async () => {
        if (!amount || isNaN(amount) || amount <= 0) {
            setError("Please enter a valid amount.");
            return;
        }
        setLoading(true);
        setError("");
        try {
            await RefreshAccessToken();
            const apiCall = transactionType === "deposit" ? DepositApi : WithdrawApi;
            const response = await apiCall({ amount });
            if (response.data.success) {
                await fetchBalance();
                setTransactionType(null);
                setAmount("");
            } else {
                setError(response.data.message || "Transaction failed.");
            }
        } catch (err) {
            console.error(`Error processing ${transactionType}:`, err);
            setError(
                err.response?.data?.message || `Failed to ${transactionType} funds.`
            );
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        const fetchData = async () => {
            await Promise.all([
                fetchOpenBoxes(),
                fetchClosedBoxes(),
                fetchSummary()
            ]);
            setBoxesLoading(false);
        };

        fetchBalance();
        setBoxesLoading(true);
        fetchData();
    }, []);

    // Render helper components
    const SkeletonLoader = () => (
        <div className="space-y-4">
            <div className="h-8 bg-gray-600 animate-pulse rounded-lg"></div>
            <div className="h-8 bg-gray-600 animate-pulse rounded-lg"></div>
            <div className="h-8 bg-gray-600 animate-pulse rounded-lg"></div>
            <div className="h-8 bg-gray-600 animate-pulse rounded-lg"></div>
        </div>
    );

    const TransactionRow = ({ transaction }) => (
        <tr className="bg-gray-750 text-sm text-gray-300">
            <td className="px-6 py-3 text-center whitespace-nowrap">
            <span className={`px-2 py-1 rounded text-xs ${
                transaction.type === "buy"
                    ? "bg-green-500/20 text-green-400"
                    : "bg-red-500/20 text-red-400"
            }`}>
                {transaction.type}
            </span>
            </td>
            <td className="px-6 py-3 text-center whitespace-nowrap">
                {formatNumber(transaction.amount)}
            </td>
            <td className="px-6 py-3 text-center whitespace-nowrap">
                ${formatNumber(transaction.price)}
            </td>
            <td className="px-6 py-3 text-center whitespace-nowrap">
                ${formatNumber(transaction.value)}
            </td>
            <td className="px-6 py-3 text-center whitespace-nowrap">
                {new Date(transaction.transaction_date).toLocaleString()}
            </td>
            {transaction.type === "sell" && (
                <>
                    <td className="px-6 py-3 text-center whitespace-nowrap text-green-400">
                        ${parseFloat(transaction.profit_loss_value).toFixed(2)}
                    </td>
                    <td className="px-6 py-3 text-center whitespace-nowrap text-green-400">
                        {parseFloat(transaction.profit_loss_percentage).toFixed(2)}%
                    </td>
                </>
            )}

            {transaction.type === "buy" && (
                <>
                    <td className="px-6 py-3 text-center whitespace-nowrap text-green-400">
                    </td>
                    <td className="px-6 py-3 text-center whitespace-nowrap text-green-400">
                    </td>
                </>
            )}

            <td className="px-6 py-3 text-center whitespace-nowrap">
                <button
                    onClick={() => handleDeleteTransaction(transaction.id)}
                    className="p-2 bg-red-600 text-white rounded-lg hover:bg-red-500 transition-all duration-300 shadow-lg hover:shadow-red-500/30 transform hover:scale-110"
                    title="Delete Transaction"
                >
                    <TrashIcon className="h-3 w-3" />
                </button>
            </td>
        </tr>
    );

    const renderTableHeaders = () => {
        if (activeTab === "open") {
            return (
                <tr className="bg-gray-700">
                    <th className="px-6 py-4 text-left text-sm font-semibold text-gray-200 whitespace-normal">
                        Coin
                    </th>
                    <th className="px-6 py-4 text-center text-sm font-semibold text-gray-200 whitespace-normal">
                        Current Price
                    </th>
                    <th className="px-6 py-4 text-center text-sm font-semibold text-gray-200 whitespace-normal">
                        Current Amount
                    </th>
                    <th className="px-6 py-4 text-center text-sm font-semibold text-gray-200 whitespace-normal">
                        Value
                    </th>
                    <th className="px-6 py-4 text-center text-sm font-semibold text-gray-200 whitespace-normal">
                        Average Buy Price
                    </th>
                    <th className="px-6 py-4 text-center text-sm font-semibold text-gray-200 whitespace-normal">
                        Profit/Loss Value
                    </th>
                    <th className="px-6 py-4 text-center text-sm font-semibold text-gray-200 whitespace-normal">
                        Profit/Loss Percentage
                    </th>
                    <th className="px-6 py-4 text-center text-sm font-semibold text-gray-200 whitespace-normal">
                        Box Age
                    </th>
                    <th className="px-6 py-4 text-right text-sm font-semibold text-gray-200 whitespace-normal">
                        <button
                            onClick={() => setShowAddTransaction(true)}
                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-500 transition-all duration-300 shadow-lg hover:shadow-blue-500/30 transform hover:scale-105"
                        >
                            Add Transaction
                        </button>
                    </th>
                </tr>
            );
        }
        return (
            <tr className="bg-gray-700">
                <th className="px-6 py-4 text-left text-sm font-semibold text-gray-200 whitespace-normal">
                    Coin
                </th>
                <th className="px-6 py-4 text-center text-sm font-semibold text-gray-200 whitespace-normal">
                Average Buy Price
                </th>
                <th className="px-6 py-4 text-center text-sm font-semibold text-gray-200 whitespace-normal">
                    Average Sell Price
                </th>
                <th className="px-6 py-4 text-center text-sm font-semibold text-gray-200 whitespace-normal">
                    Profit/Loss Percentage
                </th>
                <th className="px-6 py-4 text-center text-sm font-semibold text-gray-200 whitespace-normal">
                    Total Buy Value
                </th>
                <th className="px-6 py-4 text-center text-sm font-semibold text-gray-200 whitespace-normal">
                    Total Sell Value
                </th>
                <th className="px-6 py-4 text-center text-sm font-semibold text-gray-200 whitespace-normal">
                    Profit/Loss Value
                </th>
                <th className="px-6 py-4 text-center text-sm font-semibold text-gray-200 whitespace-normal">
                    Box Age
                </th>
            </tr>
        );
    };

    const renderTableRow = (box) => {
        const commonCoinCell = (
            <td className="px-6 py-4">
                <div className="flex items-center gap-3">
                    <a
                        href={`https://www.tradingview.com/symbols/${box.coin_symbol}USD/`}
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        <img
                            src={box.coin_icon || "../components/img/default.png"}
                            alt={box.coin_symbol}
                            className="h-8 w-8 rounded-full cursor-pointer"
                        />
                    </a>
                    <span className="font-bold text-white">
                        {box.coin_symbol}{" "}
                        <span className="font-medium text-white text-xs">
                            ({box.coin_name})
                        </span>
                    </span>
                    <motion.span
                        animate={{ rotate: expandedBoxId === box.id ? 180 : 0 }}
                        className="ml-2"
                    >
                        <ChevronDown className="h-5 w-5 text-gray-400" />
                    </motion.span>
                </div>
            </td>
        );

        if (activeTab === "open") {
            return (
                <>
                    {commonCoinCell}
                    <td className="px-6 py-4 text-gray-300 text-center">
                        ${box.current_price == 0 ? "N/A" : formatNumber(box.current_price)}
                    </td>
                    <td className="px-6 py-4 text-gray-300 text-center">
                        {formatNumber(box.amount)}
                    </td>
                    <td className="px-6 py-4 text-gray-300 text-center">
                        ${formatNumber(box.value)}
                    </td>
                    <td className="px-6 py-4 text-gray-300 text-center">
                        ${formatNumber(box.average_buy_price)}
                    </td>
                    <td
                        className={`px-6 py-4 text-center ${
                            parseFloat(box.profit_loss_value) >= 0
                                ? "text-green-400"
                                : "text-red-400"
                        }`}
                    >
                        ${parseFloat(box.profit_loss_value).toFixed(2)}
                    </td>
                    <td
                        className={`px-6 py-4 text-center ${
                            parseFloat(box.profit_loss_percentage) >= 0
                                ? "text-green-400"
                                : "text-red-400"
                        }`}
                    >
                        {parseFloat(box.profit_loss_percentage).toFixed(2)}%
                    </td>
                    <td className="px-6 py-4 text-gray-300 text-center">{box.age} days</td>
                    <td className="px-6 py-4 text-center">
                        <button
                            onClick={(e) => handleCloseBox(box.id, e)}
                            className="p-2 bg-orange-500 text-white rounded-lg hover:bg-red-500 transition-all duration-300 shadow-lg hover:shadow-red-500/30 transform hover:scale-110"
                            title="Close Box"
                        >
                            <X className="h-4 w-4" />
                        </button>
                    </td>
                </>
            );
        }
        return (
            <>
                {commonCoinCell}
                <td className="px-6 py-4 text-gray-300 text-center">
                    ${formatNumber(box.average_buy_price)}
                </td>
                <td className="px-6 py-4 text-gray-300 text-center">
                    ${formatNumber(box.average_sell_price)}
                </td>
                <td
                    className={`px-6 py-4 text-center ${
                        parseFloat(box.profit_loss_percentage) >= 0
                            ? "text-green-400"
                            : "text-red-400"
                    }`}
                >
                    {parseFloat(box.profit_loss_percentage).toFixed(2)}%
                </td>
                <td className="px-6 py-4 text-gray-300 text-center">
                    ${formatNumber(box.total_buy_value)}
                </td>
                <td className="px-6 py-4 text-gray-300 text-center">
                    ${formatNumber(box.total_sell_value)}
                </td>
                <td
                    className={`px-6 py-4 text-center ${
                        parseFloat(box.profit_loss_value) >= 0
                            ? "text-green-400"
                            : "text-red-400"
                    }`}
                >
                    ${parseFloat(box.profit_loss_value).toFixed(2)}
                </td>
                <td className="px-6 py-4 text-gray-300 text-center">{box.age} days</td>
            </>
        );
    };

    const SummaryCard = ({ title, value, percentage }) => (
        <div className="bg-gray-750 rounded-xl p-4 shadow-lg">
            <h3 className="text-gray-400 text-sm mb-2">{title}</h3>
            <div className="space-y-1">
                <div className={`text-xl font-bold ${value >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    ${Math.abs(value).toFixed(2)}
                </div>
                <div className={`text-sm ${percentage >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {percentage >= 0 ? '+' : ''}{percentage.toFixed(2)}%
                </div>
            </div>
        </div>
    );

    return (
        <div className="min-h-screen bg-gradient-to-b from-gray-900 to-gray-800">
            {/* Header Section */}
            <div className="bg-gradient-to-r from-gray-800 to-gray-900 p-5 shadow-xl">
                <motion.div
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="absolute top-8 left-8"
                >
                    <button
                        onClick={handleLogout}
                        className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-all duration-300 ease-in-out transform hover:scale-105 shadow-lg hover:shadow-red-500/30"
                    >
                        Logout
                    </button>
                </motion.div>

                <div className="flex justify-end items-start gap-3 mx-auto">
                    <div className="relative">
                        <motion.div
                            className="absolute -left-16 top-1/2 -translate-y-1/2 flex flex-col gap-3"
                            initial={{ opacity: 0, x: -20 }}
                            animate={{ opacity: 1, x: 0 }}
                        >
                            <button
                                onClick={() => setTransactionType("deposit")}
                                className="p-3 bg-green-600 text-white rounded-xl hover:bg-green-500 transition-all duration-300 shadow-lg hover:shadow-green-500/30 transform hover:scale-110"
                            >
                                <Plus className="h-5 w-5" />
                            </button>
                            <button
                                onClick={() => setTransactionType("withdraw")}
                                className="p-3 bg-red-600 text-white rounded-xl hover:bg-red-500 transition-all duration-300 shadow-lg hover:shadow-red-500/30 transform hover:scale-110"
                            >
                                <Minus className="h-5 w-5" />
                            </button>
                        </motion.div>
                        <AnimatePresence mode="wait">
                            {transactionType ? (
                                <TransactionModal
                                    transactionType={transactionType}
                                    amount={amount}
                                    setAmount={setAmount}
                                    handleTransaction={handleTransaction}
                                    loading={loading}
                                    onClose={() => setTransactionType(null)}
                                />
                            ) : (
                                <TotalBalanceCard
                                    Total_balance={totalBalance}
                                    loading={loading}
                                    formatter={formatter}
                                />
                            )}
                        </AnimatePresence>
                    </div>
                    <BalanceCards
                        USDT_balance={usdtBalance}
                        Coin_balance={coinBalance}
                        loading={loading}
                        formatter={formatter}
                    />
                </div>
            </div>

            {/* Main Body Section */}


            <div className="max-w-[85%] mx-auto px-6 py-8">
                {/* Add Summary Section */}
                {summary && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="mb-6"
                    >
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <SummaryCard
                                title="Realized Profit/Loss"
                                value={summary.realized_profit_loss}
                                percentage={summary.realized_profit_loss_percentage}
                            />
                            <SummaryCard
                                title="Unrealized Profit/Loss"
                                value={summary.unrealized_profit_loss}
                                percentage={summary.unrealized_profit_loss_percentage}
                            />
                            <SummaryCard
                                title="Total Profit/Loss"
                                value={summary.total_profit_loss}
                                percentage={summary.total_profit_loss_percentage}
                            />
                        </div>
                    </motion.div>
                )}

                <motion.div
                    className="flex justify-center gap-4 mb-6"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                >
                    <button
                        onClick={() => setActiveTab("open")}
                        className={`px-6 py-3 rounded-lg font-medium transition-all duration-300 ${
                            activeTab === "open"
                                ? "bg-blue-600 text-white shadow-lg shadow-blue-500/30"
                                : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                        }`}
                    >
                        Open Boxes
                    </button>
                    <button
                        onClick={() => setActiveTab("closed")}
                        className={`px-6 py-3 rounded-lg font-medium transition-all duration-300 ${
                            activeTab === "closed"
                                ? "bg-blue-600 text-white shadow-lg shadow-blue-500/30"
                                : "bg-gray-700 text-gray-300 hover:bg-gray-600"
                        }`}
                    >
                        Closed Boxes
                    </button>
                </motion.div>

                <AnimatePresence mode="wait">
                    <motion.div
                        key={activeTab}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="bg-gray-800 rounded-xl shadow-xl overflow-x-auto"
                    >
                        {boxesLoading ? (
                            <SkeletonLoader />
                        ) : (
                            <div className="overflow-x">
                                <table className="w-full">
                                    <thead>{renderTableHeaders()}</thead>
                                    <tbody className="divide-y divide-gray-700">
                                    {(activeTab === "open" ? openBoxes : closedBoxes).map(
                                        (box) => (
                                            <Fragment key={box.id}>
                                                <motion.tr
                                                    initial={{ opacity: 0 }}
                                                    animate={{ opacity: 1 }}
                                                    className="hover:bg-gray-700/50 transition-colors cursor-pointer"
                                                    onClick={() => handleExpand(box.id)}
                                                >
                                                    {renderTableRow(box)}
                                                </motion.tr>
                                                <AnimatePresence>
                                                    {expandedBoxId === box.id && (
                                                        <motion.tr
                                                            initial={{ opacity: 0, height: 0 }}
                                                            animate={{ opacity: 1, height: "auto" }}
                                                            exit={{ opacity: 0, height: 0 }}
                                                        >
                                                            <td colSpan="9" className="px-6 py-4 bg-gray-750">
                                                                <div className="space-y-2">
                                                                    {transactionLoading ? (
                                                                        <div className="flex justify-center py-4">
                                                                            <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                                                                        </div>
                                                                    ) : transactions[box.id]?.length > 0 ? (
                                                                        <table className="w-full">
                                                                            <thead>
                                                                            <tr className="text-left text-gray-300 text-sm">
                                                                                <th className="px-6 py-3 text-center whitespace-normal">
                                                                                    Type
                                                                                </th>
                                                                                <th className="px-6 py-3 text-center whitespace-normal">
                                                                                    Amount
                                                                                </th>
                                                                                <th className="px-6 py-3 text-center whitespace-normal">
                                                                                    Price
                                                                                </th>
                                                                                <th className="px-6 py-3 text-center whitespace-normal">
                                                                                    Total
                                                                                </th>
                                                                                <th className="px-6 py-3 text-center whitespace-normal">
                                                                                    Timestamp
                                                                                </th>
                                                                                <th className="px-6 py-3 text-center whitespace-normal">
                                                                                    Profit/Loss ($)
                                                                                </th>
                                                                                <th className="px-6 py-3 text-center whitespace-normal">
                                                                                    Profit/Loss (%)
                                                                                </th>
                                                                            </tr>
                                                                            </thead>
                                                                            <tbody className="divide-y divide-gray-700">
                                                                            {transactions[box.id].map(
                                                                                (transaction, index) => (
                                                                                    <TransactionRow
                                                                                        key={transaction.id || index}
                                                                                        transaction={transaction}
                                                                                    />
                                                                                )
                                                                            )}
                                                                            </tbody>
                                                                        </table>
                                                                    ) : (
                                                                        <p className="text-gray-400 text-center py-4">
                                                                            No transactions found for this box.
                                                                        </p>
                                                                    )}
                                                                </div>
                                                            </td>
                                                        </motion.tr>
                                                    )}
                                                </AnimatePresence>
                                            </Fragment>
                                        )
                                    )}
                                    </tbody>
                                </table>
                            </div>
                        )}
                    </motion.div>
                </AnimatePresence>
            </div>
            <AnimatePresence>
                {showAddTransaction && (
                    <AddTransactionModal
                        onClose={() => setShowAddTransaction(false)}
                        onSubmit={handleAddTransaction}
                        loading={loading}
                        openBoxes={openBoxes}
                    />
                )}
            </AnimatePresence>
            <AnimatePresence>
                {error && (
                    <ErrorModal error={error} onClose={() => setError("")}/>
                )}
            </AnimatePresence>
        </div>
    );
}

export default Dashboard;