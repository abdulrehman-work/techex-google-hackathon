import { Sparkles } from "lucide-react";

export default function ComingSoon({ title = "Coming Soon" }) {
    return (
        <div className="coming-wrapper">
            <div className="coming-card">

                <div className="coming-icon">
                    <Sparkles size={34} />
                </div>

                <h1>{title}</h1>

                <p>
                    This section is currently under development.
                    New features and analytics will appear here soon.
                </p>

                <div className="coming-loader">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>

            </div>
        </div>
    );
}