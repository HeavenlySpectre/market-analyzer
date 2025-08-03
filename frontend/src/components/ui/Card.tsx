import type { ReactNode } from "react";
import { motion } from "framer-motion";
import { clsx } from "clsx";

interface CardProps {
  children: ReactNode;
  className?: string;
  hover?: boolean;
}

const Card = ({ children, className, hover = false }: CardProps) => {
  return (
    <motion.div
      className={clsx(
        "bg-gray-900 rounded-lg border border-gray-800 p-6",
        hover && "hover:border-gray-700 transition-colors duration-200",
        className
      )}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      {children}
    </motion.div>
  );
};

export default Card;
