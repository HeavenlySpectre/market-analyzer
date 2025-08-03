import type { ReactNode } from "react";
import { motion } from "framer-motion";
import { clsx } from "clsx";

interface ButtonProps {
  children: ReactNode;
  variant?: "primary" | "secondary" | "outline";
  size?: "sm" | "md" | "lg";
  isLoading?: boolean;
  className?: string;
  disabled?: boolean;
  onClick?: () => void;
  type?: "button" | "submit" | "reset";
}

const Button = ({
  children,
  variant = "primary",
  size = "md",
  isLoading = false,
  className,
  disabled,
  onClick,
  type = "button",
}: ButtonProps) => {
  const variants = {
    primary:
      "bg-primary-600 hover:bg-primary-700 text-white border-transparent",
    secondary: "bg-gray-800 hover:bg-gray-700 text-gray-100 border-gray-700",
    outline: "bg-transparent hover:bg-gray-800 text-gray-100 border-gray-700",
  };

  const sizes = {
    sm: "px-3 py-1.5 text-sm",
    md: "px-4 py-2 text-base",
    lg: "px-6 py-3 text-lg",
  };

  return (
    <motion.button
      className={clsx(
        "inline-flex items-center justify-center rounded-lg border font-medium transition-colors duration-200",
        "focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 focus:ring-offset-gray-950",
        "disabled:opacity-50 disabled:cursor-not-allowed",
        variants[variant],
        sizes[size],
        className
      )}
      disabled={disabled || isLoading}
      whileHover={{ scale: disabled || isLoading ? 1 : 1.02 }}
      whileTap={{ scale: disabled || isLoading ? 1 : 0.98 }}
      onClick={onClick}
      type={type}
    >
      {isLoading ? (
        <>
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-current mr-2" />
          Loading...
        </>
      ) : (
        children
      )}
    </motion.button>
  );
};

export default Button;
