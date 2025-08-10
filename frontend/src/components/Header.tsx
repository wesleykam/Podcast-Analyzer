import { Headphones, BarChart3, User, HelpCircle, Clock } from "lucide-react";
import '../styles/global.css';
import './header.css';

export function Header() {
    return (
        <header className="header">
            <div className="header-container">
                {/* Logo and Title */}
                <div className="logo-title">
                    <div className="logo">
                        <Headphones className="icon" />
                        <BarChart3 className="icon" />
                    </div>
                    <h1 className="title">Podcast Analyzer</h1>
                </div>

                {/* Navigation */}
                <nav className="navigation">
                    <button
                        className="nav-button"
                        aria-label="View analysis history"
                    >
                        <Clock className="icon-small" />
                        <span>History</span>
                    </button>

                    <button
                        className="nav-button"
                        aria-label="Get help and support"
                    >
                        <HelpCircle className="icon-small" />
                        <span>Help</span>
                    </button>

                    <div className="profile-icon" tabIndex={0} role="button" aria-label="User profile menu">
                        <User className="icon-small" />
                    </div>
                </nav>

                {/* Mobile Navigation */}
                <div className="mobile-navigation">
                    <button className="nav-button" aria-label="Open menu">
                        <User className="icon-small" />
                    </button>
                </div>
            </div>
        </header>
    );
}

export default Header;
