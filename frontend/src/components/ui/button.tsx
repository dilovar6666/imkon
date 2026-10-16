import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";
import { forwardRef } from "react";
import { cn } from "../../lib/cn";

const buttonVariants = cva("button transition-transform disabled:cursor-not-allowed", {
  variants: {
    variant: {
      default: "",
      ghost: "ghost",
      light: "light",
    },
  },
  defaultVariants: { variant: "default" },
});

type ButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> & VariantProps<typeof buttonVariants> & { asChild?: boolean };

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button({ asChild = false, variant, className, ...props }, ref) {
  const Component = asChild ? Slot : "button";
  return <Component className={cn(buttonVariants({ variant }), className)} ref={ref} {...props} />;
});
