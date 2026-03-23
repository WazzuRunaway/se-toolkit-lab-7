#DA BALLS

# LMS Bot Development Plan

## Overview
This plan outlines the development of a Telegram bot for the Learning Management System (LMS). The bot will provide users with access to lab information, scores, and system status through both structured commands and natural language queries.

## Architecture
The bot follows a **testable handler architecture** where:
- Command logic is separated from Telegram transport layer
- Handlers are pure functions that take input and return text
- `--test` mode allows offline verification without Telegram
- Same handlers work for both test mode and live Telegram bot

## Project Structure
```
bot/
├── bot.py              # Entry point with --test mode
├── config.py           # Environment variable loading
├── handlers/           # Command handlers (testable)
│   ├── __init__.py
│   └── commands.py     # Basic command implementations
├── services/           # API clients (LMS, LLM)
├── pyproject.toml      # Dependencies
└── PLAN.md            # This plan
```

## Task Breakdown

### Task 1: Scaffold (Current)
- ✅ Create project structure
- ✅ Implement --test mode
- ✅ Basic command handlers with placeholder responses
- ✅ Environment configuration
- ✅ Dependencies setup

### Task 2: Backend Integration
**Goal**: Connect to LMS API for real data
- Implement LMS API client in `services/lms_client.py`
- Update handlers to fetch real data:
  - `/labs` → List available labs from API
  - `/scores <lab>` → Get scores for specific lab
  - `/health` → Check backend connectivity
- Add proper error handling for API failures
- Test with real backend data

### Task 3: Intent Routing (LLM)
**Goal**: Natural language command processing
- Implement LLM client in `services/llm_client.py`
- Create intent classification system
- Add natural language handler that:
  - Routes queries to appropriate commands
  - Extracts parameters from natural language
  - Provides helpful responses
- Examples:
  - "what labs are available" → calls `/labs`
  - "show me scores for lab-04" → calls `/scores lab-04`
  - "how am I doing" → calls `/scores` with user context

### Task 4: Telegram Integration
**Goal**: Connect handlers to Telegram bot
- Implement Telegram message handlers
- Add proper command routing
- Handle user context and conversation state
- Add error handling and user feedback
- Deploy and test in Telegram

### Task 5: Advanced Features
**Goal**: Enhanced user experience
- User session management
- Rich message formatting (Markdown/HTML)
- Interactive elements (buttons, keyboards)
- Rate limiting and spam protection
- Logging and monitoring

## Development Approach

### Testing Strategy
- **Unit tests**: Handler functions with mock data
- **Integration tests**: API client interactions
- **End-to-end tests**: Full bot interactions via --test mode
- **Manual testing**: Telegram bot verification

### Code Quality
- Type hints throughout
- Comprehensive error handling
- Clear separation of concerns
- Documentation for all public functions
- Consistent code style

### Deployment
- VM-based deployment with systemd service
- Environment-based configuration
- Log rotation and monitoring
- Graceful shutdown handling

## Risk Mitigation

### API Dependencies
- **Risk**: Backend API unavailable during development
- **Mitigation**: Mock data for testing, graceful degradation

### LLM Integration
- **Risk**: LLM API rate limits or failures
- **Mitigation**: Fallback to structured commands, caching

### Telegram Issues
- **Risk**: Bot token issues, rate limiting
- **Mitigation**: Comprehensive error handling, user feedback

## Success Criteria

### Functional
- All commands work in --test mode
- Bot responds correctly in Telegram
- Natural language queries work
- Error handling is user-friendly

### Technical
- Clean, testable code architecture
- Proper dependency management
- Environment-based configuration
- Comprehensive logging

### User Experience
- Fast response times
- Clear error messages
- Intuitive command interface
- Helpful natural language support

## Timeline
- **Task 1**: Scaffold (1-2 days)
- **Task 2**: Backend integration (2-3 days)
- **Task 3**: Intent routing (3-4 days)
- **Task 4**: Telegram integration (2-3 days)
- **Task 5**: Advanced features (2-3 days)

Total estimated time: 10-15 days with proper testing and documentation.
