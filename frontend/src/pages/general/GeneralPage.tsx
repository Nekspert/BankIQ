import { useCallback, useEffect, useState, type FC } from 'react';
import { StatisticTable } from '@/features/statistic-table/StatisticTable';
import styles from './styles.module.scss';
import TableFilterPanel from '@/features/table-filter-panel/TableFilterPanel';
import { tableArray, tableConfigs } from './constants';
import { SideMenu } from '@/features/side-menu/SideMenu';
import classNames from 'classnames';
import MenuIcon from './icons/menu-icon.svg?react';
import { useScrollamaObserver } from './hooks/useScrollamaObserver';
import { useActiveGraph } from './hooks/useActiveGraph';
import Title from '@/shared/ui/title/Title';
import { indicatorsF810Api } from '@/shared/api/form-810/indicatorsApi';

export const GeneralPage: FC = () => {
  const [selectedIds, setSelectedIds] = useState<string[]>(
    tableArray.map((it) => it.id)
  );
  const [sideMenuIsOpen, setSideMenuIsOpen] = useState(false);
  const { activeId: activeGraphId, setActiveGraphOptimized } = useActiveGraph();

  useScrollamaObserver({
    stepSelector: '.scrolly-step',
    onStepEnter: (id) => setActiveGraphOptimized(id),
    containerId: 'root',
  });

  const getInfo = async () => {
    const { data } = await indicatorsF810Api.getIndicator({
      regNum: 1481,
      date: '2019-01-01T00:00:00Z',
    });
    console.log(data);
  };
  getInfo();
  // console.log()

  useEffect(() => {
    if (!activeGraphId && selectedIds.length > 0) {
      setActiveGraphOptimized(selectedIds[0]);
    } else if (activeGraphId && !selectedIds.includes(activeGraphId)) {
      setActiveGraphOptimized(selectedIds[0] || '');
    }
  }, [selectedIds, activeGraphId, setActiveGraphOptimized]);

  const handleMenuLinkClick = useCallback(
    (id: string) => {
      setActiveGraphOptimized(id);
      document.getElementById(id)?.scrollIntoView({
        behavior: 'smooth',
        block: 'center',
      });
      setSideMenuIsOpen(false);
    },
    [setActiveGraphOptimized]
  );

  const handleApply = useCallback((ids: string[]) => setSelectedIds(ids), []);
  const handleChangeSideMenu = useCallback(
    () => setSideMenuIsOpen((prev) => !prev),
    []
  );

  return (
    <div className={styles['page__wrapper']}>
      <SideMenu
        handleClose={handleChangeSideMenu}
        tableList={tableArray}
        isOpen={sideMenuIsOpen}
        activeId={activeGraphId}
        onLinkClick={handleMenuLinkClick}
      />

      <button
        className={styles['page__menu-icon']}
        onClick={handleChangeSideMenu}
      >
        <MenuIcon />
      </button>

      <section
        id="general-page-section"
        className={classNames(styles.page, {
          [styles['page--wide']]: !sideMenuIsOpen,
        })}
      >
        <div className={styles.header}>
          <Title level={1} size="xlarge">
            Общая статистика, предоставляемая ЦБ РФ
          </Title>
        </div>

        <div style={{ marginBottom: 20 }}>
          <TableFilterPanel
            items={tableArray}
            initialSelectedIds={selectedIds}
            onApply={handleApply}
          />
        </div>

        <div className={styles.grid}>
          {tableArray.map((it) => {
            if (!selectedIds.includes(it.id)) return null;
            const config = tableConfigs[it.id];
            if (!config) return null;

            return (
              <article
                id={it.id}
                key={it.id}
                className={classNames(styles.card, 'scrolly-step')}
              >
                <StatisticTable
                  requestData={config.requestData}
                  endpoint={config.endpoint}
                  minYear={config.minYear}
                />
              </article>
            );
          })}
        </div>
      </section>
    </div>
  );
};

export default GeneralPage;
